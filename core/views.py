from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import AssignmentForm
from .models import Assignment


def home(request):
    context = {
        "page_title": "Home",
        "course_name": "CSCE A490 WebDev",
        "announcement": "Create an assignment, then follow it to its detail page.",
        "topics": ["ModelForms", "GET and POST", "Validation", "CSRF"],
    }
    return render(request, "core/home.html", context)


def about(request):
    context = {
        "page_title": "About CourseHub",
        "description": "CourseHub helps us organize our class work.",
        "items": ["Students", "Instructor"],
    }
    return render(request, "core/page.html", context)


def assignments(request, status="unfinished"):
    states = {
        "unfinished": (
            "Unfinished practice assignments",
            "No unfinished practice assignments.",
        ),
        "completed": (
            "Completed practice assignments",
            "No completed practice assignments.",
        ),
        "all": (
            "All practice assignments",
            "No practice assignments yet.",
        ),
    }
    if status not in states:
        raise Http404("Unknown assignment status.")

    tasks = Assignment.objects.all()
    if status == "unfinished":
        tasks = tasks.filter(completed=False)
    elif status == "completed":
        tasks = tasks.filter(completed=True)
    tasks = tasks.order_by("due_date", "pk")

    page_title, empty_message = states[status]
    context = {
        "page_title": page_title,
        "assignments": tasks,
        "assignment_count": tasks.count(),
        "active_status": status,
        "empty_message": empty_message,
    }
    return render(request, "core/assignments.html", context)


def assignment_detail(request, pk):
    task = get_object_or_404(Assignment, pk=pk)
    context = {
        "page_title": task.title,
        "assignment": task,
    }
    return render(request, "core/assignment_detail.html", context)


@require_http_methods(["GET", "POST"])
def assignment_create(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            task = form.save()
            return redirect("core:assignment_detail", pk=task.pk)
    else:
        form = AssignmentForm()

    context = {
        "page_title": "Add assignment",
        "form": form,
    }
    return render(request, "core/assignment_form.html", context)


def resources(request):
    context = {
        "page_title": "Resources",
        "description": "Places to continue learning.",
        "items": ["Django documentation", "Class code guides"],
    }
    return render(request, "core/page.html", context)
