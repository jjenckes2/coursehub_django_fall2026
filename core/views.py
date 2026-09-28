from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("CourseHub is Running!")

def about(request):
    return HttpResponse("CourseHub about page")

def assignments(request):
    return HttpResponse("CourseHub assignment page")

def resources(request):
    return HttpResponse("CourseHub resources page")

def page_intro(request, page_name):
    return HttpResponse(f"CourseHub {page_name} page")
