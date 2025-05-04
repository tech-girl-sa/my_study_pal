from rest_framework.serializers import ModelSerializer

from my_study_pal.courses.models import Course, Section, Message


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = ['id','title', 'description', 'tags', 'subject']


class SectionSerializer(ModelSerializer):
    class Meta:
        model = Section
        fields = ['id','title', 'description', 'course']

class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class CreateMessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ["content"]




