from django.contrib import admin

from .models import UserProfile, ChapaPayment, UploadedDocument


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "has_access", "fun_mode", "updated_at")
    search_fields = ("user__username", "user__email")


@admin.register(ChapaPayment)
class ChapaPaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "tx_ref", "status", "created_at", "access_granted_at")
    search_fields = ("tx_ref",)


@admin.register(UploadedDocument)
class UploadedDocumentAdmin(admin.ModelAdmin):
    list_display = ("user", "original_filename", "processing_status", "uploaded_at")
    search_fields = ("original_filename",)

