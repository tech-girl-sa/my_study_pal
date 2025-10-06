from django.contrib.postgres.fields import ArrayField
from django.db import models

from my_study_pal.courses.models import TopicsMixin, EntityManager
from my_study_pal.documents.models import Document





class Subject(TopicsMixin, models.Model):
    title = models.CharField("Title", max_length=300)
    token = models.CharField("Tokenized Title", max_length=300)
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

    @property
    def documents_count(self):
        return Document.objects.filter(course__in=self.courses.all()).count()


    @property
    def courses_count(self):
        return self.courses.count()

    @property
    def vector_store_name(self):
        return "subjects"

    @property
    def metadata(self):
        return {"instance_id": self.id, "user_id": self.user.id}


    class Meta:
        unique_together = ("user", "token")
