from rest_framework import filters, generics, permissions

from .api_pagination import CourseHubPagination
from .api_serializers import (
    AssignmentFilterSerializer, AssignmentSerializer, CategorySerializer,
)
from .models import Assignment, Category


class CategoryListAPI(generics.ListAPIView):
    queryset = Category.objects.order_by("name", "pk")
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = CourseHubPagination


class AssignmentListAPI(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = CourseHubPagination
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("title", "description", "category__name")
    ordering_fields = ("due_date", "title", "estimated_minutes")
    ordering = ("due_date", "pk")

    def get_queryset(self):
        queryset = Assignment.objects.select_related("owner", "category")
        params = AssignmentFilterSerializer(data=self.request.query_params.dict())
        params.is_valid(raise_exception=True)
        values = params.validated_data
        if "category" in values:
            queryset = queryset.filter(category_id=values["category"])
        if "completed" in values:
            queryset = queryset.filter(completed=values["completed"])
        return queryset


class AssignmentDetailAPI(generics.RetrieveAPIView):
    queryset = Assignment.objects.select_related("owner", "category")
    serializer_class = AssignmentSerializer
    permission_classes = (permissions.AllowAny,)
