from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from account.models import Account_HomeOwner
from account.models import Account_Professional
from account.models import Order
from account.models import All_Service
from account.models import Service_List
from account.models import Message
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
    query = request.GET.get('q')
    if query:
        serv = All_Service.objects.filter(service__icontains=query).distinct('service')
    else:
        serv = All_Service.objects.all().distinct('service')
    return render(request, "homeowners/service.html", {'serv': serv, 'query': query})




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
    serdis = All_Service.objects.filter(subservice__in=servs.values('subservice')).values('service_id')
    print(serdis.values("service"))
    s = bk  
    if request.method =="POST":
        date = request.POST.get('date')
        time = request.POST.get('time')
        number = request.POST.get('number')
        houseno = request.POST.get('houseno')
        address = request.POST.get('address')
        
        # Convert s to an instance of Account_Professional model
        professional = Account_Professional.objects.get(professional_id=s)
        current_user = request.user
        homeowner = get_object_or_404(Account_HomeOwner, username=current_user.username)
    
        serv = Order(
            date = date,
            time = time,
            number = number,
            houseno = houseno,
            address = address,
            professional_id = servs[0],  # Assign the instance to professional_id field
            homeowner_id = homeowner  # Assign the logged in homeowner to homeowner_id field
        )
        serv.save()
        order_id = serv.order_id  
        return redirect('unbook', prof_id=s, order_id=order_id)
    
    serdis = {'serdis':serdis}
    servs = {'servs': servs} 
    so = {'s': s}
    context = {**servs, **so, **serdis}
    return render(request, "homeowners/servicetime.html",context)

    
@login_required(login_url="hsignin")
def servicemanlist(request, slk):
    search_query = request.GET.get('q')
    if search_query:
        servs = Account_Professional.objects.filter(subservice=slk, address__icontains=search_query)
    else:
        servs = Account_Professional.objects.filter(subservice=slk)
    s = slk
    servs = {'servs': servs}
    so = {'s': s}
    context = {**servs, **so}
    return render(request, "homeowners/servicemanlist.html", context)

@login_required(login_url="hsignin")
def book(request,sml):
    sk = Account_Professional.objects.get(professional_id=sml)
    return render(request, "homeowners/book.html",{'sk':sk})

def unbook(request, prof_id, order_id):
    sk = Account_Professional.objects.get(professional_id=prof_id)
    ord = Order.objects.get(order_id=order_id)
    if ord.status == 'cancel':
        status = 'Cancel'
    elif ord.status == 'solve':
        status = 'Solve'
    else:
        status = 'Book'
    return render(request, "homeowners/unbook.html",{'sk':sk, 'ord':ord, 'status':status})


def KhaltiRequestView(self, request, *args, **kwargs):
    context = {
        
    }    
    return render(request, "khaltirequest.html",context)
    


@login_required(login_url="hsignin")
def activates(request, order_id):
    instance = get_object_or_404(Order, order_id=order_id)
    status = request.POST.get('status')
    message = request.POST.get('message')
    if status == 'cancel':
        instance.status = 'cancel'
        instance.message = message
        instance.save()
    elif status == 'solve':
        instance.status = 'solve'
        instance.message = message
        instance.save()
    else:
        instance.status = 'book'
        instance.message = message
        instance.save()
    return redirect("home")

@login_required(login_url="hsignin")
def notification(request):
    return render(request, "homeowners/notification.html")

@login_required(login_url="hsignin")
def profile(request):
    return render(request, "homeowners/profile.html")

@login_required(login_url="hsignin")
def bookings(request):
    ord = Order.objects.all()
    return render(request, "homeowners/bookings.html",{'ord':ord})

@login_required(login_url="hsignin")
def bookingdetails(request,od):
    ord = Order.objects.get(order_id=od)
    if ord.status == 'cancel':
        status = 'Cancel'
    elif ord.status == 'solve':
        status = 'Solve'
    else:
        status = 'Book'
    return render(request, "homeowners/bookingdetails.html",{'ord':ord, 'status':status})


def requestdetails(request,rd):
    ord = Order.objects.get(order_id=rd)
    if ord.status == 'cancel':
        status = 'Cancel'
    elif ord.status == 'solve':
        status = 'Solve'
    else:
        status = 'Book'
    return render(request, "professionals/requestdetails.html",{'ord':ord, 'status':status})


def request(request):
    ord = Order.objects.all()
    return render(request, "professionals/request.html",{'ord':ord})

def professionalprofile(request):
    return render(request, "professionals/professionalprofile.html")

def professionalnotification(request):
    return render(request, "professionals/professionalnotification.html")

@login_required(login_url="adminsignin")
def adminhomepage(request):
    h = Account_HomeOwner.objects.all().count()
    p = Account_Professional.objects.all().count()
    s = Service_List.objects.all().count()
    ho = {'h': h}
    po = {'p': p}
    so = {'s': s}
    context = {**ho, **po, **so}
    return render(request, "admin/adminhomepage.html",context)

@login_required(login_url="adminsignin")
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

@login_required(login_url="adminsignin")
def admincreatesubservice(request):
    servs = Service_List.objects.all().distinct('service_list') 
    if request.method =="POST":
        service = request.POST.get('service')
        subservice = request.POST.get('subservice')
        photo = request.FILES.get('photo')
        desc = request.POST.get('desc')
        if All_Service.objects.filter(subservice=subservice).exists():
                messages.info(request,'Sorry! Sub-Service Already Exist')
                return redirect('admincreatesubservice')
        else:    
            serv = All_Service(
                service = service,
                subservice = subservice,
                photo = photo,
                desc = desc   
            )
            serv.save()
            messages.info(request,'New Sub-Service Created')
    return render(request, "admin/admincreatesubservice.html",{'servs':servs})


@login_required(login_url="adminsignin")
def adminmessage(request):
    msg = Message.objects.all() 
  
    for i in msg:
        print(msg) 
    return render(request, "admin/adminmessage.html",{'msg':msg})

@login_required(login_url="adminsignin")
def adminorderdetail(request,ok):
    ord = Order.objects.get(order_id=ok) 
    return render(request, "admin/adminorderdetail.html",{'ord':ord})

@login_required(login_url="adminsignin")
def adminprofile(request):
    return render(request, "admin/adminprofile.html")

@login_required(login_url="adminsignin")
def adminservicedetail(request, pk):
    serv = All_Service.objects.get(service_id=pk)
    if request.method == "POST":
        subservice = request.POST.get('subservice')
        photo = request.POST.get('photo')
        desc = request.POST.get('desc')
        
        # Update the existing instance with the new values
        serv.subservice = subservice
        if photo:
            serv.photo = photo
        serv.desc = desc
        serv.save()
        messages.info(request,'Sucessfull Update!!!')
        
    return render(request, "admin/adminservicedetail.html", {'serv': serv})

@login_required(login_url="adminsignin")
def adminservicelist(request):
    # serv = All_Service.objects.exclude(service=True)
    serv = All_Service.objects.all()
    return render(request, "admin/adminservicelist.html",{'serv':serv})

@login_required(login_url="adminsignin")
def adminservicemandetail(request,pok):
    po = Account_Professional.objects.get(professional_id=pok)
    return render(request, "admin/adminservicemandetail.html",{'po':po})

@login_required(login_url="adminsignin")
def adminservicemanlist(request):
    po = Account_Professional.objects.all()
    return render(request, "admin/adminservicemanlist.html",{'po':po})

@login_required(login_url="adminsignin")
def adminuserdetail(request,hk):
    ho = Account_HomeOwner.objects.get(homeowner_id=hk)
    return render(request, "admin/adminuserdetail.html",{'ho':ho})

@login_required(login_url="adminsignin")
def adminusermanlist(request):
    ho =Account_HomeOwner.objects.all()
    return render(request, 'admin/adminusermanlist.html',{'ho':ho})

@login_required(login_url="adminsignin")
def adminvieworder(request):
    ord = Order.objects.all()
    return render(request, "admin/adminvieworder.html",{'ord':ord})

@login_required(login_url="adminsignin")
def adminnotification(request):
    return render(request, "admin/adminnotification.html")

@login_required(login_url="adminsignin")
def deleteservice(request, service_id):
    serv = All_Service.objects.filter(service_id = service_id).delete() 
    return redirect("adminservicelist")

@login_required(login_url="adminsignin")
def deleteservicelist(request, servicelist_id):
    serv = Service_List.objects.filter(servicelist_id = servicelist_id).delete() 
    return redirect("admincreateservice")

@login_required(login_url="adminsignin")
def deleteuser(request, homeowner_id):
    ho = Account_HomeOwner.objects.filter(homeowner_id = homeowner_id).delete() 
    return redirect("adminusermanlist")

@login_required(login_url="adminsignin")
def deleteserviceman(request, professional_id):
    po = Account_Professional.objects.filter(professional_id = professional_id).delete() 
    return redirect("adminservicemanlist")

@login_required(login_url="adminsignin")
def deleteorder(request, order_id):
    ord = Order.objects.filter(order_id = order_id).delete() 
    return redirect("adminvieworder")

@login_required(login_url="adminsignin")
def deletemsg(request, msg_id):
    msg = Message.objects.filter(msg_id = msg_id).delete() 
    return redirect("adminmessage")

@login_required(login_url="adminsignin")
def activate(request, professional_id):
    instance = get_object_or_404(Account_Professional, professional_id=professional_id)
    instance.status = not instance.status
    instance.save()
    return redirect("adminservicemanlist")

@login_required(login_url="adminsignin")
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
    if request.method =="POST":
        message = request.POST.get('message')
        print(message)
        username = ""
        try:
            username = Account_HomeOwner.objects.get(username=request.user.username)
        except Account_HomeOwner.DoesNotExist:
            try:
                username = Account_Professional.objects.get(username=request.user.username)
            except Account_Professional.DoesNotExist:
                return HttpResponse("Error: User not found.")
        
        messages = Message(
            homeowner_id=username, 
            message=message,
        )
        messages.save() 
          
    return HttpResponseRedirect("")
  















