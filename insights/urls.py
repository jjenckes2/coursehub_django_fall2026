from django.urls import path
from . import views

app_name = "insights"

urlpatterns = [
    path("grade-dashboard/", views.grade_dashboard, name="dashboard"),
]
