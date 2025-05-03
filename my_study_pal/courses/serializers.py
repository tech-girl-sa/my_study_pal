from rest_framework.serializers import ModelSerializer,ListSerializer

from my_study_pal.courses.models import Course, Section


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ['id','title', 'description', 'tags', 'subject']


class SectionSerializer(ModelSerializer):
    class Meta:
        model = Section
        fields = ['id','title', 'description', 'course']


