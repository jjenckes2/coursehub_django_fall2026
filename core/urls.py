from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("assignments/", views.assignments, name="assignments"),
    path("assignments/new/", views.assignment_create, name="assignment_create"),
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
    path(
        "assignments/<int:pk>/edit/",
        views.assignment_update,
        name="assignment_update",
    ),
    path(
        "assignments/<int:pk>/delete/",
        views.assignment_delete,
        name="assignment_delete",
    ),
    path("resources/", views.resources, name="resources"),
]
