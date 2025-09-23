from rest_framework.mixins import CreateModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from my_study_pal.users.models import UserInfo

from my_study_pal.users.serializers import UserInfoSerializer


class UserInfoViewSet(CreateModelMixin, RetrieveModelMixin,  UpdateModelMixin, GenericViewSet):
    serializer_class = UserInfoSerializer
    queryset= UserInfo.objects.all()

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(user__id=self.request.user.id)

    def get_object(self):
        return self.get_queryset().first()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance =self.get_object()
        if not instance:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
