from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from my_study_pal.courses.views import CoursesViewset, SectionsViewset

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

app_name = "courses"

router.register(r"courses", CoursesViewset, basename="course")
router.register(r"sections", SectionsViewset, basename="section")
urlpatterns = [
    path('', include(router.urls)),
]
