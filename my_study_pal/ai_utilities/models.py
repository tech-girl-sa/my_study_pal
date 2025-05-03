from django.db import models




class AiModel(models.Model):
    name = models.CharField("Name", max_length=300)
    token = models.CharField("Tokenized Name", max_length=300, unique=True)
    configuration = models.JSONField("Description", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    def save(self, *args, **kwargs):
        self.token = ''.join(char for char in self.name.lower().replace(" ","_") if char.isalnum() or char =="_")
        super().save()


class Settings(models.Model):
    temperature = models.FloatField("Temperature", blank=True)
    ai_model = models.ForeignKey("AiModel", verbose_name="AI Model", on_delete=models.SET_NULL,
                                 related_name="settings", null=True)
    user = models.ForeignKey("users.User", verbose_name="User", on_delete=models.CASCADE, related_name="settings")
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
