from rest_framework import serializers

from my_study_pal.ai_utilities.models import Settings


class UserQuestionSerializer(serializers.Serializer):
    user_question = serializers.CharField()


class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ["ai_model", "temperature", "translation_language"]



