from django.shortcuts import render
from django.http import HttpResponse
from user.models import Account_HomeOwner
from user.models import All_Service

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
    serv = All_Service.objects.all().distinct('service') 
    return render(request, "homeowners/service.html",{'serv':serv})

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

def bookingdetails(request):
    return render(request, "homeowners/bookingdetails.html")

def requestdetails(request):
    return render(request, "professionals/requestdetails.html")

def request(request):
    return render(request, "professionals/request.html")

def professionalprofile(request):
    return render(request, "professionals/professionalprofile.html")

def professionalnotification(request):
    return render(request, "professionals/professionalnotification.html")

def adminhomepage(request):
    return render(request, "admin/adminhomepage.html")

def admincreateservice(request):
    if request.method =="POST":
        service = request.POST.get('service')
        subservice = request.POST.get('subservice')
        photo = request.POST.get('photo')
        desc = request.POST.get('desc')
        
        serv = All_Service(
            service = service,
            subservice = subservice,
            photo = photo,
            desc = desc   
        )
        print(desc)
        serv.save()
    return render(request, "admin/admincreateservice.html")

def adminmessage(request):
    return render(request, "admin/adminmessage.html")

def adminorderdetail(request):
    return render(request, "admin/adminorderdetail.html")

def adminprofile(request):
    return render(request, "admin/adminprofile.html")

def adminservicedetail(request):
    serv = All_Service.objects.all()
    return render(request, "admin/adminservicedetail.html",{'serv':serv})

def adminservicelist(request):
    serv = All_Service.objects.all() 
    return render(request, "admin/adminservicelist.html",{'serv':serv})

def adminservicemandetail(request):
    return render(request, "admin/adminservicemandetail.html")

def adminservicemanlist(request):
    return render(request, "admin/adminservicemanlist.html")

def adminuserdetail(request):
    return render(request, "admin/adminuserdetail.html")

def adminusermanlist(request):
    # ho: Account_HomeOwner.objects.all()
    
    # context = {
    #     'ho':ho,
    # }
    return render(request, 'admin/adminusermanlist.html')

def adminvieworder(request):
    return render(request, "admin/adminvieworder.html")

def adminnotification(request):
    return render(request, "admin/adminnotification.html")















