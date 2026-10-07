from django.contrib import admin
from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "due_date", "completed", "estimated_minutes")
    list_filter = ("completed", "due_date")
    search_fields = ("title", "description")
    ordering = ("due_date", "pk")