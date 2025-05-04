import os
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins
from my_study_pal.courses.models import Course
from my_study_pal.documents.models import Document
from my_study_pal.documents.serializers import DocumentsSerializer, DocumentUploadSerializer


class DocumentsViewset(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = DocumentsSerializer
    queryset = Document.objects.all()

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
        return super().create(request, *args, **kwargs)


    def perform_create(self, serializer):
        course_id = self.request.query_params.get('course_id', None)
        file = self.request.data.get("file", None)
        filename = os.path.splitext(file.name)[0]
        if course_id:
            course = Course.objects.get(id=course_id)
            serializer.save(user= self.request.user,course= course, title=filename)
        else:
            #TODO add logic to identify/create the course if course id is not provided that will match
            # the case where user uploads the document from documents page
            serializer.save(user=self.request.user)






