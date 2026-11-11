from django.contrib import admin

from .models import AssignmentResult


@admin.register(AssignmentResult)
class AssignmentResultAdmin(admin.ModelAdmin):
    list_display = (
        "assignment", "cohort", "learner_code", "grade_percent", "actual_minutes",
    )
    list_editable = ("grade_percent", "actual_minutes")
    list_filter = ("cohort", "assignment")
    search_fields = ("assignment__title", "learner_code")
    list_select_related = ("assignment",)
    ordering = ("assignment_id", "learner_code")
