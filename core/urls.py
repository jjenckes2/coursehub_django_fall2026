from django.urls import path
from . import views 

urlpatterns = [
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("assignments", views.assignments, name="assignments"),
    path("resources", views.resources, name="resources"),
    path("<str:page_name>", views.page_intro, name="page intro")
]