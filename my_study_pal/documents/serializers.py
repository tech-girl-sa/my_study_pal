import os

from rest_framework import serializers
from my_study_pal.documents.models import Document


class DocumentsSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(source='course.subject', read_only=True)

    class Meta:
        model = Document
        fields = ["id", "title", "file", "course", "subject", "created_at"]


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'created_at']
        read_only_fields = ['id', 'created_at', 'title']


