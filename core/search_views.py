from django.db.models import Q
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Assignment, Category
from .search_forms import SearchForm


@require_GET
def search(request):
    form = SearchForm(request.GET)
    query = ""
    assignment_results = Assignment.objects.none()
    category_results = Category.objects.none()

    if form.is_valid():
        query = form.cleaned_data["q"]
        if query:
            assignment_results = (
                Assignment.objects.select_related("category")
                .filter(
                    Q(title__icontains=query)
                    | Q(description__icontains=query)
                    | Q(category__name__icontains=query)
                )
                .order_by("due_date", "pk")
            )
            category_results = Category.objects.filter(name__icontains=query).order_by("name")

    return render(request, "core/search.html", {
        "page_title": "Search CourseHub",
        "search_form": form,
        "query": query,
        "assignment_results": assignment_results,
        "category_results": category_results,
        "assignment_count": assignment_results.count(),
        "category_count": category_results.count(),
    })
