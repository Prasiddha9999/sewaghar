from django.shortcuts import render, get_list_or_404, redirect
from django.http import HttpResponse
from user.models import Account_HomeOwner
from user.models import Account_Professional
from user.models import Order
from user.models import All_Service
from user.models import Message

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
    h = Account_HomeOwner.objects.all().count()
    p = Account_Professional.objects.all().count()
    s = All_Service.objects.all().count()
    ho = {'h': h}
    po = {'p': p}
    so = {'s': s}
    context = {**ho, **po, **so}
    return render(request, "admin/adminhomepage.html",context)

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
    msg = Message.objects.all() 
    return render(request, "admin/adminmessage.html",{'msg':msg})

def adminorderdetail(request,ok):
    ord = Order.objects.get(order_id=ok) 
    return render(request, "admin/adminorderdetail.html",{'ord':ord})

def adminprofile(request):
    return render(request, "admin/adminprofile.html")

def adminservicedetail(request,pk):
    serv = All_Service.objects.get(service_id=pk) 
    return render(request,"admin/adminservicedetail.html",{'serv':serv})

def adminservicelist(request):
    serv = All_Service.objects.all() 
    return render(request, "admin/adminservicelist.html",{'serv':serv})

def adminservicemandetail(request,pok):
    po = Account_Professional.objects.get(professional_id=pok)
    return render(request, "admin/adminservicemandetail.html",{'po':po})

def adminservicemanlist(request):
    po = Account_Professional.objects.all()
    return render(request, "admin/adminservicemanlist.html",{'po':po})

def adminuserdetail(request,hk):
    ho = Account_HomeOwner.objects.get(homeowner_id=hk)
    return render(request, "admin/adminuserdetail.html",{'ho':ho})

def adminusermanlist(request):
    ho =Account_HomeOwner.objects.all()
    return render(request, 'admin/adminusermanlist.html',{'ho':ho})

def adminvieworder(request):
    ord = Order.objects.all()
    return render(request, "admin/adminvieworder.html",{'ord':ord})

def adminnotification(request):
    return render(request, "admin/adminnotification.html")


def deleteservice(request, service_id):
    serv = All_Service.objects.filter(service_id = service_id).delete() 
    return redirect("adminservicelist")

def deleteuser(request, homeowner_id):
    ho = Account_HomeOwner.objects.filter(homeowner_id = homeowner_id).delete() 
    return redirect("adminusermanlist")

def deleteserviceman(request, professional_id):
    po = Account_Professional.objects.filter(professional_id = professional_id).delete() 
    return redirect("adminservicemanlist")

def deleteorder(request, order_id):
    ord = Order.objects.filter(order_id = order_id).delete() 
    return redirect("adminvieworder")

def deletemsg(request, msg_id):
    msg = Message.objects.filter(msg_id = msg_id).delete() 
    return redirect("adminmessage")













