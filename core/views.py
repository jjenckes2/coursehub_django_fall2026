from django.contrib import messages
from django.contrib.auth.decorators import login_required  # added for Oct 21 lecture
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import AssignmentForm, AssignmentUpdateForm
from .models import Assignment


def home(request):
    context = {
        "page_title": "Home",
        "course_name": "CSCE A490 WebDev",
        # added for Oct 21 lecture: introduce authentication and sessions.
        "announcement": "Browse assignments, then log in to make changes.",
        "topics": ["Login", "Sessions", "Protected views", "Logout"],
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


# added for Oct 21 lecture: require login before creating an assignment.
@login_required
@require_http_methods(["GET", "POST"])
def assignment_create(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, "Assignment created.")
            return redirect("core:assignment_detail", pk=task.pk)
    else:
        form = AssignmentForm()

    context = {
        "page_title": "Add assignment",
        "form": form,
        "form_action": reverse("core:assignment_create"),
        "cancel_url": reverse("core:assignments_by_status", kwargs={"status": "all"}),
        "submit_label": "Save assignment",
        "form_description": "New assignments start unfinished. Description is optional.",
    }
    return render(request, "core/assignment_form.html", context)


# added for Oct 21 lecture: require login before looking up or editing an assignment.
@login_required
@require_http_methods(["GET", "POST"])
def assignment_update(request, pk):
    task = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        form = AssignmentUpdateForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            messages.success(request, "Assignment updated.")
            return redirect("core:assignment_detail", pk=task.pk)
    else:
        form = AssignmentUpdateForm(instance=task)

    context = {
        "page_title": "Edit assignment",
        "form": form,
        "form_action": reverse("core:assignment_update", kwargs={"pk": task.pk}),
        "cancel_url": reverse("core:assignment_detail", kwargs={"pk": task.pk}),
        "submit_label": "Save changes",
        "form_description": "Update the details or change the completion status.",
    }
    return render(request, "core/assignment_form.html", context)


# added for Oct 21 lecture: require login before confirming or deleting an assignment.
@login_required
@require_http_methods(["GET", "POST"])
def assignment_delete(request, pk):
    task = get_object_or_404(Assignment, pk=pk)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Assignment deleted.")
        return redirect("core:assignments_by_status", status="all")

    context = {
        "page_title": "Delete assignment",
        "assignment": task,
    }
    return render(request, "core/assignment_confirm_delete.html", context)


def resources(request):
    context = {
        "page_title": "Resources",
        "description": "Places to continue learning.",
        "items": ["Django documentation", "Class code guides"],
    }
    return render(request, "core/page.html", context)
