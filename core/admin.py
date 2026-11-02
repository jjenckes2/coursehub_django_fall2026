from django.contrib import admin

from .models import Assignment, Category

class AssignmentInline(admin.TabularInline):
    model = Assignment
    fields = ("title", "owner", "due_date", "completed")
    extra = 0
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = (AssignmentInline,)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title", "category", "owner", "due_date",
        "completed", "estimated_minutes",
    )
    list_display_links = ("title",)
    list_editable = ("completed","estimated_minutes")
    list_filter = ("category","completed", "due_date")
    search_fields = ("title", "description", "category__name")
    ordering = ("due_date", "pk")
    list_select_related = ("category","owner")
