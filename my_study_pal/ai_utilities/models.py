import os

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from google import genai
from openai import OpenAI, api_key


class AiModel(models.Model):
    class AiAgentNameChoices(models.TextChoices):
         OPEN_AI= "open_ai", "Open AI"
         GEMINI = "gemini", "Gemini"
    name = models.CharField("AI Agent Name", max_length=300, choices=AiAgentNameChoices.choices)
    class AiAgentModelChoices(models.TextChoices):
         GPT_4O_MINI= "gpt-4o-mini", "gpt-4o-mini"
         GEMINI_2_FLASH = "gemini-2.0-flash", "gemini-2.0-flash"
    model = models.CharField("Ai Agent Model", max_length=300, choices=AiAgentModelChoices.choices)
    token = models.CharField("Tokenized Name", max_length=300, unique=True)
    configuration = models.JSONField("Configuration", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    def save(self, *args, **kwargs):
        self.token = ''.join(char
                             for char in f'{self.name}_{self.model.lower().replace("-","_").replace(".", "_")}'
                             if char.isalnum() or char =="_")
        super().save()


    @property
    def api_key(self):
        keys_mapping = {
            self.AiAgentNameChoices.OPEN_AI: "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY"
        }
        return os.environ.get(keys_mapping[self.name])

    @property
    def client(self):
        clients_mapping = {
            self.AiAgentNameChoices.OPEN_AI: OpenAI,
            self.AiAgentNameChoices.GEMINI: genai.Client
        }
        return clients_mapping[self.name](api_key= self.api_key)


class Settings(models.Model):
    temperature = models.FloatField("Temperature", blank=True)
    ai_model = models.ForeignKey("AiModel", verbose_name="AI Model", on_delete=models.SET_NULL,
                                 related_name="settings", null=True)

    class LanguageChoices(models.TextChoices):
        ENGLISH = "en", "English"
        ARABIC = "ar", "Arabic"
        FRENCH = "fr", "French"
        GERMAN = "de", "German"
        SPANISH = "es", "Spanish"
        ITALIAN = "it", "Italian"
        PORTUGUESE = "pt", "Portuguese"
        RUSSIAN = "ru", "Russian"
        CHINESE_SIMPLIFIED = "zh", "Chinese (Simplified)"
        JAPANESE = "ja", "Japanese"
        KOREAN = "ko", "Korean"
        DUTCH = "nl", "Dutch"
        SWEDISH = "sv", "Swedish"
        TURKISH = "tr", "Turkish"
        POLISH = "pl", "Polish"
        HINDI = "hi", "Hindi"
        BENGALI = "bn", "Bengali"
        UKRAINIAN = "uk", "Ukrainian"
        GREEK = "el", "Greek"
        HEBREW = "he", "Hebrew"
    translation_language =  models.CharField(
    max_length=5,
    choices=LanguageChoices.choices,
    default=LanguageChoices.ENGLISH
    )
    temperature = models.FloatField(
        default=0.7,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ],
        help_text="Controls AI creativity: 0 = focused/deterministic, 1 = highly creative."
    )
    user = models.OneToOneField("users.User", verbose_name="User", on_delete=models.CASCADE, related_name="settings")
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

