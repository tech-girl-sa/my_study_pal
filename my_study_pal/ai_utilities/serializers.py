from rest_framework import serializers


class UserQuestionSerializer(serializers.Serializer):
    user_question = serializers.CharField()
