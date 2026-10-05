from django.shortcuts import render
from django.http import HttpResponse

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
    return render(request, "core/about.html", context)

def resources(request):
    context = {
        "page_title": "Resources",
        "description": "Places to continue learning.",
        "items": ["Django documentation", "Class code guides"],
    }
    return render(request, "core/resources.html", context)
