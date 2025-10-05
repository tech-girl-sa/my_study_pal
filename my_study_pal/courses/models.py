from django.contrib.postgres.fields import ArrayField
from django.db import models


class EntityManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_archived=False)


class TopicsMixin:

    def save(self, *args, **kwargs):
        from my_study_pal.ai_utilities.vector_store_utils import VectorStoreManager
        """#TODO increament token index when trying to save existing one in DB"""
        self.token = ''.join(char for char in self.title.lower().replace(" ","_") if char.isalnum() or char =="_")
        super().save()
        VectorStoreManager(self.vector_store_name).add_vector(self)


class Course(TopicsMixin, models.Model):
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

    @property
    def vector_store_name(self):
        return "courses"

    @property
    def metadata(self):
        return {"instance_id": self.id, "subject_id": self.subject.id,
                                       "user_id": self.subject.user.id}



class Section(TopicsMixin ,models.Model):
    title = models.CharField("Title", max_length=300)
    token = models.CharField("Tokenized Title", max_length=300, unique=True)
    description = models.TextField("Description", max_length=2000, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    course = models.ForeignKey("Course", verbose_name="Course", on_delete=models.CASCADE, related_name="sections")
    objects = EntityManager()

    @property
    def vector_store_name(self):
        return "sections"

    @property
    def metadata(self):
        return {"instance_id": self.id, "course_id": self.course.id,
                                        "user_id": self.course.subject.user.id}


class Chunk(models.Model):
    content = models.TextField("content", max_length=2000, blank=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    section = models.ForeignKey("Section", verbose_name="section", on_delete=models.CASCADE, related_name="chunks")

    def save(self, *args, **kwargs):
        from my_study_pal.ai_utilities.vector_store_utils import VectorStoreManager
        super().save()
        VectorStoreManager(self.vector_store_name).add_vector(self)

    @property
    def vector_store_name(self):
        return "chunks"


    @property
    def metadata(self):
        return {"instance_id": self.id, "course_id": self.section.course.id,
                                        "user_id": self.section.course.subject.user.id, "section_id":self.section.id,
                                      "document_id":self.section.course.document.id}




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
    related_message = models.OneToOneField("courses.Message", verbose_name="Related Message",
                                           on_delete=models.CASCADE, null=True, blank=True, related_name="ai_response")
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    @property
    def vector_store_name(self):
        return "messages"

    @property
    def metadata(self):
        return {"instance_id": self.id, "sendder": self.sender,
                "user_id": self.user.id, "ai_model": self.ai_model,
                "section_id": self.section.id, "course_id": self.section.course.id}

    def save(self, *args, **kwargs):
        from my_study_pal.ai_utilities.vector_store_utils import VectorStoreManager
        super().save()
        VectorStoreManager(self.vector_store_name).add_vector(self)
