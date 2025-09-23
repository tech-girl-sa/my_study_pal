from django.db import models


def get_file_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/uploads/user_<id>/<filename>
    return f'uploads/user_{instance.user.id}/{filename}'


class Document(models.Model):
    title = models.CharField("Title", max_length=300)
    file = models.FileField(upload_to=get_file_path)
    course = models.OneToOneField("courses.Course", verbose_name="course", on_delete=models.CASCADE,
                                  related_name="document", null=True, blank=True)
    user = models.ForeignKey("users.User", verbose_name="User", on_delete=models.CASCADE, related_name="documents")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
