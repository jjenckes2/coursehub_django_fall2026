from django.contrib import admin
from .models import Assignment
from django.contrib.auth import get_user_model

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    # add here for Oct 26 lecture
    list_display = ("title", "due_date", "completed", "estimated_minutes")
    list_filter = ("completed", "due_date")
    search_fields = ("title", "description")
    ordering = ("due_date", "pk")
