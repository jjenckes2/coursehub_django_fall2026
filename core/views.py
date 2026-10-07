from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import Assignment

def home(request):
   context = {
       "page_title": "Home",
       "course_name": "CSCE A490 WebDev",
       "announcement": "On <strong>Wednesday</strong> will cover shared templates",
       "topics": ["Templates", "Context", "Static Files"],
   }
   return render(request, "core/home.html", context)

def about(request):
    context = {
        "page_title": "About CourseHub",
        "course_name": "CSCE A490 WebDev",
        "description": "CourseHub helps us keep our class organized",
        "items": ["Students", "Instructor"]
    }
    return render(request, "core/page.html", context)

#add assignment view and assignment detail

def resources(request):
    context = {
        "page_title": "Resources",
        "description": "Places to continue learning.",
        "items": ["Django documentation", "Class code guides"],
    }
    return render(request, "core/page.html", context)
