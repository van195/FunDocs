from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile, UploadedDocument


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, min_length=3, max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["has_access", "fun_mode", "chapa_email"]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["fun_mode"]


class DocumentUploadResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDocument
        fields = ["id", "original_filename", "processing_status", "processing_error", "uploaded_at"]


class DocumentListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDocument
        fields = ["id", "original_filename", "processing_status", "processing_error", "uploaded_at"]


class ChatAskSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    question = serializers.CharField(min_length=1, max_length=4000)

