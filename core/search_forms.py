from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(label="Search CourseHub", required=False, max_length=100)
