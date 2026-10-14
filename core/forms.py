from django import forms

from .models import Assignment


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ("title", "description", "due_date", "estimated_minutes")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
            "estimated_minutes": forms.NumberInput(
                attrs={"min": 1, "max": 480},
            ),
        }
        labels = {
            "estimated_minutes": "Estimated time in minutes",
        }
        help_texts = {
            "title": "Use a short, specific title (up to 120 characters).",
            "description": "Optional: describe what needs to be done.",
            "due_date": "Choose the assignment's due date.",
            "estimated_minutes": "Enter a whole number from 1 to 480.",
        }

    def clean_estimated_minutes(self):
        minutes = self.cleaned_data["estimated_minutes"]
        if not 1 <= minutes <= 480:
            raise forms.ValidationError("Enter a duration from 1 to 480 minutes.")
        return minutes
