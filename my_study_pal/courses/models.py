from django.contrib.postgres.fields import ArrayField
from django.db import models
from my_study_pal.subjects.models import EntityManager


class Course(models.Model):
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
    subject = models.ForeignKey("subjects.Subject", verbose_name="Subject", on_delete=models.CASCADE, related_name="courses")
    objects = EntityManager()

    def save(self, *args, **kwargs):
        """#TODO increament token index when trying to save existing one in DB"""
        self.token = ''.join(char for char in self.title.lower().replace(" ","_") if char.isalnum() or char =="_")
        super().save()


class Section(models.Model):
    title = models.CharField("Title", max_length=300)
    token = models.CharField("Tokenized Title", max_length=300, unique=True)
    description = models.TextField("Description", max_length=2000, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    course = models.ForeignKey("Course", verbose_name="Course", on_delete=models.CASCADE, related_name="sections")
    objects = EntityManager()

    def save(self, *args, **kwargs):
        """#TODO increament token index when trying to save existing one in DB"""
        self.token = ''.join(char for char in self.title.lower().replace(" ","_") if char.isalnum() or char =="_")
        super().save()


class Message(models.Model):
    class SenderChoices(models.TextChoices):
        user = "user", "User"
        ai_agent = "ai_model", "AI Model"
    sender = models.CharField("Sender", choices=SenderChoices.choices, max_length=50)
    content = models.TextField("Content", max_length=5000)
    section = models.ForeignKey("courses.Section", verbose_name="Section", on_delete=models.CASCADE,
                                related_name="messages")
    user = models.ForeignKey("users.User", verbose_name="User", on_delete=models.CASCADE, related_name="messages",
                             blank=True, null=True)
    ai_model = models.ForeignKey("ai_utilities.AiModel", verbose_name="AI Model", on_delete=models.SET_NULL,
                                 related_name="messages", null=True, blank=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
