from components.calendar.calendar import Calendar
from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def inicio(request):
    return render(request, "inicio.html")
