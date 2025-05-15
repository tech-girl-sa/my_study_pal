from django.urls import path
from my_study_pal.ai_utilities.views import ClassifyMessage

app_name = "ai_utilities"

urlpatterns = [
    path('classify_message/', ClassifyMessage.as_view(), name='classify_message'),
]
