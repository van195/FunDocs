# Generated manually for scaffold completeness.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ChapaPayment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "tx_ref",
                    models.CharField(max_length=128, unique=True),
                ),
                (
                    "amount",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "currency",
                    models.CharField(max_length=16),
                ),
                (
                    "status",
                    models.CharField(
                        default="pending",
                        help_text="pending/success/failed",
                        max_length=32,
                    ),
                ),
                (
                    "chapa_reference",
                    models.CharField(blank=True, max_length=128, null=True),
                ),
                (
                    "access_granted_at",
                    models.DateTimeField(blank=True, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "has_access",
                    models.BooleanField(default=False),
                ),
                (
                    "fun_mode",
                    models.BooleanField(default=False),
                ),
                (
                    "chapa_email",
                    models.EmailField(blank=True, null=True, max_length=254),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UploadedDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "original_filename",
                    models.CharField(max_length=255),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="api.models.document_upload_path"
                    ),
                ),
                (
                    "processing_status",
                    models.CharField(
                        default="pending",
                        help_text="pending/done/error",
                        max_length=32,
                    ),
                ),
                (
                    "extracted_text_path",
                    models.CharField(blank=True, max_length=512, null=True),
                ),
                (
                    "rag_data_dir",
                    models.CharField(blank=True, max_length=512, null=True),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

