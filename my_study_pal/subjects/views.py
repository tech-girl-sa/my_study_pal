from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from my_study_pal.subjects.models import Subject
from my_study_pal.subjects.serializers import SubjectSerializer
from django_filters import rest_framework as dfilters
from django.db.models import Q



class ArrayContainsFilter(dfilters.Filter):

    def filter(self, qs, value):
        if value:
            items = value.split(",")
            lookup = f"{self.field_name}__contains"
            query = Q(**{lookup:[items[0]]})
            for item in items[1:]:
                query = query| Q(**{lookup:[item]})
            qs=qs.filter(query)
        return qs


class SubjectFilter(dfilters.FilterSet):
    tags = ArrayContainsFilter(field_name="tags")

    class Meta:
        model = Subject
        fields = ["tags"]


class SubjectsViewset(ModelViewSet):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()
    filter_backends = [ DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['title', 'date_created']
    ordering = ['title']
    filterset_class = SubjectFilter

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(user__id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.is_archived = True
        instance.save()

    @swagger_auto_schema(
        operation_description="Filter subjects by tags",
        manual_parameters=[
            openapi.Parameter(
                'tags', openapi.IN_QUERY, description="Comma-separated list of tags",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

