from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter

from my_study_pal.courses.views import CoursesViewset, SectionsViewset, CreateSectionMessageView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

app_name = "courses"

router.register(r"courses", CoursesViewset, basename="course")
router.register(r"sections", SectionsViewset, basename="section")
urlpatterns = [
    path('', include(router.urls)),
    path('sections/<int:section_id>/messages', CreateSectionMessageView.as_view({"post":"create", "get":"list"})
         ,name="messages")
]
