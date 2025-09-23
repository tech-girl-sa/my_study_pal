from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models


class User(AbstractUser):
    """
    Default custom user model for My Study Pal.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    ...


class UserInfo(models.Model):
    user = models.OneToOneField("User", verbose_name="User", on_delete=models.CASCADE, related_name="user_info")
    age = models.PositiveIntegerField("How old are you?", blank=True)
    country = models.CharField("User's Country", max_length=200, blank=True)
    class AcademicLevelChoices(models.TextChoices):
        MIDDLE_SCHOOL = "middle_school", "Middle School"
        HIGH_SCHOOL = "high_school", "High School"
        UNIVERSITY = "university", "University"
        VOCATIONAL_FORMATION = "vocational_formation", "Vocational/Formation"
        SELF_LEARNING = "self_learning", "Self-learning"
        OTHER = "other", "Other"

    academic_level = models.CharField("What is your current academic level?", max_length=50, blank=True, choices= AcademicLevelChoices.choices)
    institution_name = models.CharField("Institution Name", max_length=200, blank=True)
    current_year = models.CharField("Current year or semester", blank=True, max_length=150)
    subjects = models.CharField("Subjects you're studying", max_length=300, blank=True)
    goals = models.TextField("What are your learning goals", max_length=600, blank=True)

    class RequiredHelpChoices(models.TextChoices):
        SUMMARIZE = "summarize_course", "Summarize my courses"
        TRANSLATE = "translate", "Translate material"
        EXPLAIN = "explain", "Explain Difficult concepts"
        ASK = "ask", "Ask questions via chat"
        GENERATE_QUIZZES = "generate_quizzes", "Generate quizzes"

    required_help = ArrayField(
        models.CharField(max_length=100, choices=RequiredHelpChoices.choices),
        size=5,
        blank=True,
        default=list
    )




