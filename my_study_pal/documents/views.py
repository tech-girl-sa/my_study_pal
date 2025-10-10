import os
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, filters
from django_filters import rest_framework as dfilters
from my_study_pal.courses.models import Course
from my_study_pal.documents.document_processing import DocumentProcessor
from my_study_pal.documents.models import Document
from my_study_pal.documents.serializers import DocumentsSerializer, DocumentUploadSerializer
from django_filters.rest_framework import DjangoFilterBackend

from my_study_pal.subjects.models import Subject


class DocumentFilter(dfilters.FilterSet):
    course = dfilters.ModelChoiceFilter(queryset=Course.objects.all(), label="Course")
    subject = dfilters.ModelChoiceFilter(queryset=Subject.objects.all(), label="Subject",
                                         field_name="course__subject")

    class Meta:
        model = Document
        fields = [ "course", "subject"]


class DocumentsViewset(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = DocumentsSerializer
    queryset = Document.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter,filters.SearchFilter]
    ordering_fields = ['title', 'created_at']
    ordering = ['title']
    search_fields = ['title']
    filterset_class = DocumentFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return DocumentsSerializer
        else:
            return DocumentUploadSerializer

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(user__id=self.request.user.id)


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'course', openapi.IN_QUERY,
                description="Optional course ID from query",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ]
    )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        extra_data = getattr(self, "extra_data","")
        response.data = {
                "document": response.data,
                "extra_data": extra_data
            }
        return response


    def perform_create(self, serializer):
        course_id = self.request.query_params.get('course_id', None)
        file = self.request.data.get("file", None)
        filename = os.path.splitext(file.name)[0]
        document = serializer.save(user=self.request.user, title=filename)
        ai_agent_token = "gemini_gemini_2_0_flash"
        self.extra_data = DocumentProcessor(document).process_document(ai_agent_token, course_id, self.request.user.id)

    @swagger_auto_schema(
        operation_description="Filter Documents",
        manual_parameters=[
            openapi.Parameter(
                'course', openapi.IN_QUERY, description="Filter by course",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'subject', openapi.IN_QUERY, description="Filter by subject", type=openapi.TYPE_INTEGER
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)






