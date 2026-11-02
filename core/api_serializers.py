from rest_framework import serializers

from .models import Assignment, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = fields


class AssignmentSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    category_name = serializers.CharField(
        source="category.name", read_only=True, allow_null=True,
    )

    class Meta:
        model = Assignment
        fields = (
            "id", "title", "description", "due_date", "completed",
            "estimated_minutes", "category", "category_name", "owner",
        )
        read_only_fields = fields


class AssignmentFilterSerializer(serializers.Serializer):
    category = serializers.IntegerField(min_value=1, required=False)
    completed = serializers.BooleanField(required=False)
