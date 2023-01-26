from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, "home.html")

def blog(request):
    return render(request, "blog.html")

def aboutus(request):
    return render(request, "aboutus.html")

def privacypolicy(request):
    return render(request, "privacypolicy.html")

def termsandcondition(request):
    return render(request, "termsandcondition.html")

def service(request):
    return render(request, "homeowners/service.html")

def subservice(request):
    return render(request, "homeowners/subservice.html")

def servicetime(request):
    return render(request, "homeowners/servicetime.html")

def servicemanlist(request):
    return render(request, "homeowners/servicemanlist.html")

def book(request):
    return render(request, "homeowners/book.html")

def unbook(request):
    return render(request, "homeowners/unbook.html")

def notification(request):
    return render(request, "homeowners/notification.html")

def profile(request):
    return render(request, "homeowners/profile.html")

def bookings(request):
    return render(request, "homeowners/bookings.html")

def bookingdetail(request):
    return render(request, "homeowners/bookingdetail.html")

