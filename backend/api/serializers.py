from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile, UploadedDocument, QuizAttempt


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


class QuizGenerateSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    num_questions = serializers.IntegerField(required=False, default=5, min_value=3, max_value=10)


class QuizAnswerItemSerializer(serializers.Serializer):
    question_id = serializers.CharField(max_length=64)
    selected_index = serializers.IntegerField(min_value=0, max_value=3)


class QuizSubmitSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    answers = QuizAnswerItemSerializer(many=True)

    def validate_answers(self, value):
        ids = [a["question_id"] for a in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Duplicate question_id in answers.")
        return value

