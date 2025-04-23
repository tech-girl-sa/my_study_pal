from django.urls import path
from django.views.generic import TemplateView

app_name = "main"
urlpatterns = [
    path("", TemplateView.as_view(template_name="main/home.html"), name="home"),
    path(
        "signup/",
        TemplateView.as_view(template_name="main/signup.html"),
        name="signup",
    ),
    path(
        "onboarding/step1",
        TemplateView.as_view(template_name="main/onboarding1.html"),
        name="onboarding1",
    ),
    path(
        "onboarding/step2",
        TemplateView.as_view(template_name="main/onboarding2.html"),
        name="onboarding2",
    ),
    path(
            "onboarding/step3",
            TemplateView.as_view(template_name="main/onboarding3.html"),
            name="onboarding3",
        ),
    path(
                "onboarding/step4",
                TemplateView.as_view(template_name="main/onboarding4.html"),
                name="onboarding4",
            ),

    path(
                "dashboard",
                TemplateView.as_view(template_name="main/dashboard.html"),
                name="dashboard",
            ),

    path(
        "subjects",
        TemplateView.as_view(template_name="main/subjects.html"),
        name="dashboard",
    ),
path(
        "subjects/<int:subject_id>/",
        TemplateView.as_view(template_name="main/subject_details.html"),
        name="dashboard",
    ),
path(
        "courses",
        TemplateView.as_view(template_name="main/courses.html"),
        name="dashboard",
    ),
path(
        "courses/<int:course_id>/",
        TemplateView.as_view(template_name="main/course_details.html"),
        name="dashboard",
    ),
    ]
