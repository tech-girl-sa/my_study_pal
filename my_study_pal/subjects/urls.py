from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from my_study_pal.subjects.views import SubjectsViewset

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

app_name = "subjects"

router.register(r"subjects", SubjectsViewset, basename="subject")
urlpatterns = [
    path('', include(router.urls)),
]
