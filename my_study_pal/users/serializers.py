from rest_framework import serializers

from my_study_pal.users.models import UserInfo


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        exclude = ['user']


