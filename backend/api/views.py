import os
from decimal import Decimal
from typing import Any
from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .models import ChapaPayment, UploadedDocument, UserProfile
from .permissions import IsPaid
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    DocumentUploadResponseSerializer,
    DocumentListItemSerializer,
    ChatAskSerializer,
)

from .services import (
    ask_groq_about_doc,
    chapa_initialize_payment,
    chapa_verify_payment,
    extract_text_from_file,
    chunk_text,
    save_rag_artifacts,
    parse_chapa_callback_payload,
    validate_extension,
    now_utc,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(
            {"id": user.id, "username": user.username, "email": user.email},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        return Response(UserProfileSerializer(profile).data, status=status.HTTP_200_OK)


class MePreferencesUpdateView(APIView):
    def patch(self, request):
        profile = UserProfile.objects.get(user=request.user)
        ser = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(UserProfileSerializer(profile).data, status=status.HTTP_200_OK)


class ChapaPaymentCreateView(APIView):
    def post(self, request):
        profile = UserProfile.objects.get(user=request.user)
        if profile.has_access:
            return Response(
                {"detail": "You already have access. No payment needed."},
                status=status.HTTP_200_OK,
            )

        if not request.user.email:
            return Response(
                {"detail": "Your account is missing an email. Please re-register with an email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tx_ref = f"user_{request.user.id}_{os.urandom(6).hex()}"
        amount = Decimal(os.environ.get("CHAPA_AMOUNT", "10"))
        currency = os.environ.get("CHAPA_CURRENCY", "USD")

        payment = ChapaPayment.objects.create(
            user=request.user,
            tx_ref=tx_ref,
            amount=amount,
            currency=currency,
            status="pending",
        )

        try:
            result = chapa_initialize_payment(user=request.user, tx_ref=tx_ref)
        except Exception as e:
            payment.status = "failed"
            payment.save(update_fields=["status"])
            return Response(
                {
                    "detail": "Failed to initialize Chapa payment.",
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.chapa_reference = tx_ref
        payment.save(update_fields=["chapa_reference"])

        if not result.get("authorization_url"):
            payment.status = "failed"
            payment.save(update_fields=["status"])
            return Response(
                {
                    "detail": "Chapa did not return an authorization_url.",
                    "chapa_response": result.get("chapa_response"),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"tx_ref": tx_ref, "authorization_url": result.get("authorization_url")},
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class ChapaPaymentCallbackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Chapa typically posts JSON or form-encoded fields.
        payload: Any = request.data
        tx_ref, status_norm = parse_chapa_callback_payload(payload)
        if not tx_ref:
            return Response({"detail": "Missing tx_ref"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = ChapaPayment.objects.get(tx_ref=tx_ref)
        except ChapaPayment.DoesNotExist:
            return Response({"detail": "Unknown tx_ref"}, status=status.HTTP_404_NOT_FOUND)

        payment.status = status_norm
        if status_norm == "success":
            profile = UserProfile.objects.get(user=payment.user)
            profile.has_access = True
            profile.save(update_fields=["has_access"])
            payment.access_granted_at = now_utc()

        payment.save(update_fields=["status", "access_granted_at"])

        return Response({"ok": True}, status=status.HTTP_200_OK)


class ChapaPaymentVerifyLatestView(APIView):
    

    def post(self, request):
        profile = UserProfile.objects.get(user=request.user)
        if profile.has_access:
            return Response({"detail": "Access already granted."}, status=status.HTTP_200_OK)

        payment = (
            ChapaPayment.objects.filter(user=request.user)
            .order_by("-created_at")
            .first()
        )
        if not payment:
            return Response({"detail": "No payment found for this user."}, status=404)

        try:
            verify = chapa_verify_payment(tx_ref=payment.tx_ref)
        except Exception as e:
            return Response(
                {"detail": "Failed to verify payment with Chapa.", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        status_norm = verify.get("status") or "unknown"
        payment.status = status_norm
        if status_norm == "success":
            profile.has_access = True
            profile.save(update_fields=["has_access"])
            payment.access_granted_at = now_utc()

        payment.save(update_fields=["status", "access_granted_at"])

        return Response(
            {"status": status_norm, "has_access": profile.has_access},
            status=status.HTTP_200_OK,
        )


class DocumentUploadView(APIView):
    permission_classes = [IsPaid]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            return Response({"detail": "Missing `file` in multipart/form-data."}, status=400)

        validate_extension(f.name)

        doc = UploadedDocument.objects.create(
            user=request.user,
            original_filename=f.name,
            file=f,
            processing_status="pending",
        )

        try:
            extracted = extract_text_from_file(doc)
            chunks = chunk_text(extracted)
            save_rag_artifacts(doc, chunks)

            doc.processing_status = "done"
            doc.processing_error = None
            doc.processed_at = now_utc()
            doc.extracted_text_path = os.path.join(
                os.path.basename(os.path.dirname(doc.file.name)),
                "extracted_text.txt",
            )
            doc.rag_data_dir = os.path.join("rag", f"user_{doc.user_id}", f"doc_{doc.id}")
            doc.save(
                update_fields=[
                    "processing_status",
                    "processing_error",
                    "processed_at",
                    "extracted_text_path",
                    "rag_data_dir",
                ]
            )
        except Exception as e:
            doc.processing_status = "error"
            doc.processing_error = str(e)
            doc.save(update_fields=["processing_status", "processing_error"])
            return Response(
                {"detail": f"Failed to process document: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            DocumentUploadResponseSerializer(doc).data,
            status=status.HTTP_201_CREATED,
        )


class DocumentListView(APIView):
    permission_classes = [IsPaid]

    def get(self, request):
        docs = UploadedDocument.objects.filter(user=request.user).order_by("-uploaded_at")
        return Response(
            {"documents": DocumentListItemSerializer(docs, many=True).data},
            status=status.HTTP_200_OK,
        )


class ChatAskView(APIView):
    permission_classes = [IsPaid]

    def post(self, request):
        ser = ChatAskSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        document_id = ser.validated_data["document_id"]
        question = ser.validated_data["question"]

        doc = UploadedDocument.objects.get(id=document_id, user=request.user)
        if doc.processing_status != "done":
            return Response(
                {
                    "detail": "Document is not processed yet.",
                    "processing_status": doc.processing_status,
                    "processing_error": doc.processing_error,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = UserProfile.objects.get(user=request.user)
        try:
            answer = ask_groq_about_doc(doc=doc, question=question, fun_mode=bool(profile.fun_mode))
            return Response({"answer": answer}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": "Chat failed.", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

