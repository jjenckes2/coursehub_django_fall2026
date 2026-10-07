from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    #add paths here for assignments and assignment detail
    
    path("resources/", views.resources, name="resources"),
]