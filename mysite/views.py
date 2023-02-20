from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from user.models import Account_HomeOwner
from user.models import Account_Professional
from user.models import Order
from user.models import All_Service
from user.models import Service_List
from user.models import Message
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


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

@login_required(login_url="hsignin")
def service(request):
    serv = All_Service.objects.all().distinct('service') 
    return render(request, "homeowners/service.html",{'serv':serv})

@login_required(login_url="hsignin")
def subservice(request,sk):
    servs = All_Service.objects.filter(service=sk)
    s = sk
    servs = {'servs': servs}
    so = {'s': s}
    context = {**servs, **so}
    
    return render(request, "homeowners/subservice.html",context)

@login_required(login_url="hsignin")
def servicetime(request,bk):
    servs = Account_Professional.objects.filter(professional_id=bk)
    s = bk   
    if request.method =="POST":
        date = request.POST.get('date')
        time = request.POST.get('time')
        number = request.POST.get('number')
        houseno = request.POST.get('houseno')
        address = request.POST.get('address')
       
        
        serv = Order(
            date = date,
            time = time,
            number = number,
            houseno = houseno,
            address = address,
            professional_id = s
            
        )
        serv.save()
    
    servs = {'servs': servs}
    
    so = {'s': s}
    context = {**servs, **so}
    print(servs)
    return render(request, "homeowners/servicetime.html",context)
    
@login_required(login_url="hsignin")
def servicemanlist(request,slk):
    servs = Account_Professional.objects.filter(subservice=slk)
    s = slk
   
    print(s)
  
    servs = {'servs': servs}
    so = {'s': s}
    context = {**servs, **so}
    return render(request, "homeowners/servicemanlist.html",context)

@login_required(login_url="hsignin")
def book(request,sml):
    sk = Account_Professional.objects.get(professional_id=sml)
    return render(request, "homeowners/book.html",{'sk':sk})

@login_required(login_url="hsignin")
def unbook(request):
    return render(request, "homeowners/unbook.html")

@login_required(login_url="hsignin")
def notification(request):
    return render(request, "homeowners/notification.html")

@login_required(login_url="hsignin")
def profile(request):
    return render(request, "homeowners/profile.html")

@login_required(login_url="hsignin")
def bookings(request):
    return render(request, "homeowners/bookings.html")

@login_required(login_url="hsignin")
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
    servs = Service_List.objects.all().distinct('service_list') 
    if request.method =="POST":
        service_list = request.POST.get('service_list')
        if Service_List.objects.filter(service_list=service_list).exists():
                messages.info(request,'Sorry! Service Already Exist')
                return redirect('admincreateservice')
        else:    
            serv = Service_List(
                service_list = service_list 
            )
            serv.save()
            messages.info(request,'New Service Created')
    return render(request, "admin/admincreateservice.html",{'servs':servs})

def admincreatesubservice(request):
    servs = Service_List.objects.all().distinct('service_list') 
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
        serv.save()
    return render(request, "admin/admincreatesubservice.html",{'servs':servs})



def adminmessage(request):
    msg = Message.objects.all() 
  
    for i in msg:
        print(msg) 
    return render(request, "admin/adminmessage.html",{'msg':msg})

def adminorderdetail(request,ok):
    ord = Order.objects.get(order_id=ok) 
    return render(request, "admin/adminorderdetail.html",{'ord':ord})

def adminprofile(request):
    return render(request, "admin/adminprofile.html")

def adminservicedetail(request,pk):
    serv = All_Service.objects.get(service_id=pk)
    # if request.method =="POST":
    #     service = request.POST.get('service')
    #     subservice = request.POST.get('subservice')
    #     photo = request.POST.get('photo')
    #     desc = request.POST.get('desc')
        
    #     serv = All_Service(
    #         service = service,
    #         subservice = subservice,
    #         photo = photo,
    #         desc = desc   
    #     )
    #     print(desc)
    #     serv.save() 
    return render(request,"admin/adminservicedetail.html",{'serv':serv})

def adminservicelist(request):
    # serv = All_Service.objects.exclude(service=True)
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

def deleteservicelist(request, servicelist_id):
    serv = Service_List.objects.filter(servicelist_id = servicelist_id).delete() 
    return redirect("admincreateservice")

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

def activate(request, professional_id):
    instance = get_object_or_404(Account_Professional, professional_id=professional_id)
    instance.status = not instance.status
    instance.save()
    return redirect("adminservicemanlist")

def update_my_model(request, service_id):
    servs = Account_Professional.objects.filter(service_id = service_id)
    if request.method =="POST":       
        serv = All_Service(request.POST, servs=servs)         
        if serv.is_valid():
            serv.save()
            return redirect('update_my_model')
    else:
        serv = All_Service(servs=servs) 
    return render(request, 'adminservicedetail', {'serv': serv})



def usermessage(request):
    #   professional_id = Account_Professional.objects.get(professional_id = professional_id)
      if request.method =="POST":
          message = request.POST.get('message')
        #   homeowner_id = Account_HomeOwner.objects.get(homeowner_id = request.user.username)
         
          
          messages = Message(
            #  homeowner_id=homeowner_id, 
             message = message,
              
          )
          messages.save() 
      return HttpResponseRedirect("")














