from django.db import models




class AiModel(models.Model):
    name = models.CharField("Name", max_length=300)
    token = models.CharField("Tokenized Name", max_length=300, unique=True)
    configuration = models.JSONField("Configuration", blank=True, null=True)
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


class VectorStore(models.Model):
    path = models.CharField("Path of Store", max_length=300)
    text = models.TextField("Origin Text", max_length=5000)
    section = models.OneToOneField("courses.Section", verbose_name="Section", on_delete=models.CASCADE,
                                related_name="vector_store")
    document = models.ForeignKey("documents.Document", verbose_name="Document", on_delete=models.CASCADE,
                                related_name="vector_stores")
    created_at = models.DateTimeField("Created at", auto_now_add=True)



class VectorChunk(models.Model):
    text = models.CharField("Text of Chunk", max_length=800)
    message = models.ForeignKey("courses.message", verbose_name="Message" ,on_delete=models.CASCADE,
                                related_name="messages")
    section = models.ForeignKey("courses.Section", verbose_name="Section", on_delete=models.CASCADE,
                      related_name="vector_chunks")
    vector_store = models.ForeignKey("VectorStore", verbose_name="Vector Store", on_delete=models.CASCADE,
                                related_name="vector_chunks")
    metadata = models.JSONField("Metadata", blank=True, null=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True)

