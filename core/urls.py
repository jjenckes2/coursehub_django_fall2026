from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("assignments/", views.assignments, name="assignments"),
    path("resources/", views.resources, name="resources"),
]