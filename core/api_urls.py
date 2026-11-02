from django.urls import path

from . import api_views


app_name = "api"

urlpatterns = [
    path("categories/", api_views.CategoryListAPI.as_view(), name="category-list"),
    path("assignments/", api_views.AssignmentListAPI.as_view(), name="assignment-list"),
    path("assignments/<int:pk>/", api_views.AssignmentDetailAPI.as_view(), name="assignment-detail"),
]
