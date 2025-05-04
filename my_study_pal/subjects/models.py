from django.contrib.postgres.fields import ArrayField
from django.db import models

from my_study_pal.documents.models import Document


class EntityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class Subject(models.Model):
    title = models.CharField("Title", max_length=300)
    token = models.CharField("Tokenized Title", max_length=300, unique=True)
    description = models.TextField("Description", max_length=2000, blank=True)
    tags = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    user = models.ForeignKey("users.User", verbose_name="User", on_delete=models.CASCADE, related_name="subjects")
    objects = EntityManager()

    def save(self, *args, **kwargs):
        """#TODO increament token index when trying to save existing one in DB"""
        self.token = ''.join(char for char in self.title.lower().replace(" ","_") if char.isalnum() or char =="_")
        super().save()

    @property
    def documents_count(self):
        return Document.objects.filter(course__in=self.courses.all()).count()


    @property
    def courses_count(self):
        return self.courses.count()

