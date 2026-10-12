from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("assignments/", views.assignments, name="assignments"),
    path(
        "assignments/status/<slug:status>/",
        views.assignments,
        name="assignments_by_status",
    ),
    path(
        "assignments/<int:pk>/",
        views.assignment_detail,
        name="assignment_detail",
    ),
    path("resources/", views.resources, name="resources"),
]
