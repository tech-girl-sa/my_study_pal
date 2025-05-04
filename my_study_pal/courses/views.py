from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, decorators, response, viewsets, mixins
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from django_filters import rest_framework as dfilters
from my_study_pal.courses.models import Course, Section, Message
from my_study_pal.courses.serializers import CourseSerializer, SectionSerializer, MessageSerializer, \
    CreateMessageSerializer
from my_study_pal.subjects.models import Subject
from my_study_pal.subjects.views import ArrayContainsFilter



class CourseFilter(dfilters.FilterSet):
    tags = ArrayContainsFilter(field_name="tags")
    subject = dfilters.ModelChoiceFilter(queryset=Subject.objects.all(), label="Subject")

    class Meta:
        model = Course
        fields = ["tags", "subject"]



class CoursesViewset(ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    filter_backends = [ DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['title', 'created_at']
    ordering = ['title']
    filterset_class = CourseFilter

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(subject__user__id=self.request.user.id)

    def perform_destroy(self, instance):
        instance.is_archived = True
        instance.save()

    @swagger_auto_schema(
        operation_description="Filter Courses",
        manual_parameters=[
            openapi.Parameter(
                'tags', openapi.IN_QUERY, description="Comma-separated list of tags",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'subject', openapi.IN_QUERY, description="Filter by subject", type=openapi.TYPE_INTEGER
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        responses={200: SectionSerializer}
    )
    @decorators.action(detail=True, methods=['get'])
    def sections(self, request, *args, **kwargs):
        sections = self.get_object().sections
        if sections:
            serializer = SectionSerializer(sections, many=True)
            return response.Response(serializer.data)
        return response.Response({"detail": "No sections in this course."}, status=404)




class SectionsViewset(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = SectionSerializer
    queryset = Section.objects.all()

    def perform_destroy(self, instance):
        instance.is_archived = True
        instance.save()




class CreateSectionMessageView(mixins.CreateModelMixin, mixins.ListModelMixin ,viewsets.GenericViewSet):
    serializer_class = CreateMessageSerializer
    queryset = Message.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return MessageSerializer
        else:
            return CreateMessageSerializer

    def get_queryset(self):
        section_id =  self.kwargs["section_id"]
        return self.queryset.filter(section__id=section_id)

    def perform_create(self, serializer):
        section = Section.objects.get(id=self.kwargs["section_id"])
        serializer.save(user= self.request.user, sender= Message.SenderChoices.user,
                        section= section)

    #TODO return response of the AI instead of the user message
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


def identify_section():
    """Identify to which section the message belongs using AI"""
    pass



class CreateDashboardMessageView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = CreateMessageSerializer

    def perform_create(self, serializer):
        section = identify_section()
        serializer.save(user=self.request.user, sender=Message.SenderChoices.user,
                        section=section)

    # TODO return response of the AI instead of the user message
    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
