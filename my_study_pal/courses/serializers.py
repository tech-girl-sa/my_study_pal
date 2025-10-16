from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField

from my_study_pal.courses.models import Course, Section, Message


class CourseSerializer(ModelSerializer):
    first_section_id = SerializerMethodField()
    subject_title = CharField(source="subject.title", read_only=True)
    document_title = CharField(source="document.title", read_only=True)

    def get_first_section_id(self, obj):
        first_section = obj.sections.first()
        if not first_section:
            section= Section(title="Main Section", description="Main section for the course", course=obj )
            section.save()
            return section.id
        return first_section.id

    class Meta:
        model = Course
        fields = ['id','title', 'description', 'tags', 'subject_title','subject', 'document', 'document_title',
                  'created_at', 'first_section_id']
        read_only_fields = ['document']


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




