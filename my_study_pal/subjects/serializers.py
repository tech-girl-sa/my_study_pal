from rest_framework import serializers
from my_study_pal.subjects.models import Subject



class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ['id','title', 'description', 'tags', 'documents_count', 'courses_count']
