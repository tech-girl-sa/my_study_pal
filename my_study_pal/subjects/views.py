from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from my_study_pal.subjects.models import Subject
from my_study_pal.subjects.serializers import SubjectSerializer
from django_filters import rest_framework as dfilters



class ArrayContainsFilter(dfilters.Filter):

    def filter(self, qs, value):
        if value:
            lookup = f"{self.field_name}__contains"
            return qs.filter(**{lookup:[value]})
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

