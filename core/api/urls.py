from django.urls import path

from . import views


app_name = "api"

urlpatterns = [
    path("categories/", views.CategoryListAPI.as_view(), name="category-list"),
    path("assignments/", views.AssignmentListAPI.as_view(), name="assignment-list"),
    path("assignments/<int:pk>/", views.AssignmentDetailAPI.as_view(), name="assignment-detail"),
]
