from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from my_study_pal.documents.views import DocumentsViewset

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

app_name = "documents"

router.register(r"documents", DocumentsViewset, basename="document")

urlpatterns = [
    path('', include(router.urls)),

]
