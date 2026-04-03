import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    has_access = models.BooleanField(default=False)
    fun_mode = models.BooleanField(default=False)

   
    chapa_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"profile<{self.user_id}>"


class ChapaPayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tx_ref = models.CharField(max_length=128, unique=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=16)

    status = models.CharField(
        max_length=32,
        default="pending",
        help_text="pending/success/failed",
    )

    chapa_reference = models.CharField(max_length=128, blank=True, null=True)
    access_granted_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"payment<{self.tx_ref}>"


def document_upload_path(instance: "UploadedDocument", filename: str) -> str:
   
    return f"uploads/user_{instance.user_id}/document_{uuid.uuid4().hex}/{filename}"


class UploadedDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    original_filename = models.CharField(max_length=255)
    file = models.FileField(upload_to=document_upload_path)

   
    processing_status = models.CharField(
        max_length=32, default="pending", help_text="pending/done/error"
    )
    extracted_text_path = models.CharField(max_length=512, blank=True, null=True)
    rag_data_dir = models.CharField(max_length=512, blank=True, null=True)
    processing_error = models.TextField(blank=True, null=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"doc<{self.id}> by user<{self.user_id}>"

