from django.urls import path
from my_study_pal.ai_utilities.views import ClassifyMessage, SettingsView
from rest_framework.routers import DefaultRouter

app_name = "ai_utilities"
router = DefaultRouter()
router.register(r'settings', SettingsView, basename='settings')
urlpatterns = [
    path('classify_message/', ClassifyMessage.as_view(), name='classify_message'),
    path('settings/', SettingsView.as_view({"post":"update","get":"retrieve"}), name='settings'),
    path('settings/ai_model_choices/', SettingsView.as_view({'get': 'ai_model_choices'}), name='ai_model_choices'),
    path('settings/language_choices/', SettingsView.as_view({'get': 'language_choices'}), name='language_choices'),

]
