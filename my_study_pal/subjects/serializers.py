from rest_framework.serializers import ModelSerializer
from my_study_pal.subjects.models import Subject



class SubjectSerializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id','title', 'description', 'tags']
