from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    RegisterView,
    MeView,
    MePreferencesUpdateView,
    ChapaPaymentCreateView,
    ChapaPaymentCallbackView,
    ChapaPaymentVerifyLatestView,
    DocumentUploadView,
    DocumentListView,
    ChatAskView,
    QuizGenerateView,
    QuizSubmitView,
    QuizHistoryView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="refresh"),

    path("me/", MeView.as_view(), name="me"),
    path("me/preferences/", MePreferencesUpdateView.as_view(), name="me-preferences"),

    path("payments/chapa/create/", ChapaPaymentCreateView.as_view(), name="chapa-create"),
    path("payments/chapa/callback/", ChapaPaymentCallbackView.as_view(), name="chapa-callback"),
    path("payments/chapa/verify-latest/", ChapaPaymentVerifyLatestView.as_view(), name="chapa-verify-latest"),

    path("documents/upload/", DocumentUploadView.as_view(), name="document-upload"),
    path("documents/", DocumentListView.as_view(), name="document-list"),

    path("chat/ask/", ChatAskView.as_view(), name="chat-ask"),

    path("quiz/generate/", QuizGenerateView.as_view(), name="quiz-generate"),
    path("quiz/submit/", QuizSubmitView.as_view(), name="quiz-submit"),
    path("quiz/history/", QuizHistoryView.as_view(), name="quiz-history"),
]

