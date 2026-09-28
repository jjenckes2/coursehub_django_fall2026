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

def assignments(request):
    return HttpResponse("CourseHub assignment page")

def resources(request):
    return HttpResponse("CourseHub resources page")

def page_intro(request, page_name):
    return HttpResponse(f"CourseHub {page_name} page")
