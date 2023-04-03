from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from account.models import Account_HomeOwner
from account.models import Account_Professional
from account.models import Order
from account.models import All_Service
from account.models import Service_List
from account.models import Notification
from account.models import Message
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime
from django.contrib import messages as django_messages
from  django.conf import settings
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import make_password
from account.models import User
from django.contrib.auth.hashers import check_password
import random



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
    
    sk = Account_Professional.objects.get(professional_id=bk)
    sk_service = sk.subservice
    servicedata = All_Service.objects.get(subservice=sk_service)
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
        notification = Notification.objects.create(
                notification= f"Hey {professional.full_name}, you have received a new Request from {homeowner.full_name}.",
                classification="Professional",
                professional_id = professional 
            )
        notification.save()
        notifications = Notification.objects.create(
                notification= f"Hey {homeowner.full_name}, You have booked Professionals {professional.full_name}.",
                classification="HomeOwner",
                homeowner_id = homeowner 
            )
        notifications.save()
        notificationss = Notification.objects.create(
                notification= f"{homeowner.full_name}, book Professionals '{professional.full_name}' for service {servicedata.service}-{servicedata.subservice}.",
                classification="Admin",
            )
        notificationss.save()
        order_id = serv.order_id  
        return redirect('unbook', prof_id=s, order_id=order_id)
    
    serdis = {'serdis':serdis}
    servs = {'servs': servs} 
    servicedata = {'servicedata': servicedata} 
    so = {'s': s}
    sk = {'sk':sk}
    context = {**servs, **so, **serdis, **servicedata, **sk}
    return render(request, "homeowners/servicetime.html",context)

    
@login_required(login_url="hsignin")
def servicemanlist(request, slk):
    servicedata = All_Service.objects.get(subservice=slk)
    servs = Account_Professional.objects.filter(subservice=slk).order_by('-ratings')
    context = {'servs': servs, 'servicedata': servicedata}
    return render(request, "homeowners/servicemanlist.html", context)



@login_required(login_url="hsignin")
def book(request,sml):
    sk = Account_Professional.objects.get(professional_id=sml)
    sk_service = sk.subservice
    servicedata = All_Service.objects.get(subservice=sk_service)
    return render(request, "homeowners/book.html",{'sk':sk, 'servicedata':servicedata})

@login_required(login_url="hsignin")
def unbook(request, prof_id, order_id):
    sk = Account_Professional.objects.get(professional_id=prof_id)
    sk_service = sk.subservice
    servicedata = All_Service.objects.get(subservice=sk_service)
    ord = Order.objects.get(order_id=order_id)

    if ord.status == 'cancel':
        status = 'Cancel'
    elif ord.status == 'solve':
        status = 'Solve'
    else:
        status = 'Book'
    return render(request, "homeowners/unbook.html",{'sk':sk, 'ord':ord, 'status':status, 'servicedata':servicedata})

@login_required(login_url="hsignin")
def activates(request, order_id):
    instance = get_object_or_404(Order, order_id=order_id)
    status = request.POST.get('status')
    message = request.POST.get('message')
    totalhour = request.POST.get('totalhour')
    print(message)
    print("DSfsdf")
    
    if status == 'cancel':
        instance.status = 'cancel'
        instance.message = message
        instance.totaltimehour = totalhour
        instance.save()
        ord = Order.objects.get(order_id=order_id)
        homeowner = Account_HomeOwner.objects.get(homeowner_id=ord.homeowner_id.homeowner_id)
        professional = Account_Professional.objects.get(professional_id=ord.professional_id.professional_id)
        notification = Notification.objects.create(
            notification= f"Hey {professional.full_name}, your Request id {ord.order_id} has been Cancelled by {homeowner.full_name}.",
            classification="Professional",
            professional_id =  professional
            )
        notification.save()
        notifications = Notification.objects.create(
            notification= f"Hey {homeowner.full_name}, You Cancelled the Booking id {ord.order_id}.",
            classification="HomeOwner",
            homeowner_id = homeowner
            )
        notifications.save()
        notificationss = Notification.objects.create(
            notification= f"{homeowner.full_name}, cancel the Bookings id {ord.order_id} for service.",
            classification="Admin",
            )
        notificationss.save()
    elif status == 'solve':
        instance.status = 'solve'
        instance.message = message
        instance.totaltimehour = totalhour
        instance.save()
        ord = Order.objects.get(order_id=order_id)
        homeowner = Account_HomeOwner.objects.get(homeowner_id=ord.homeowner_id.homeowner_id)
        professional = Account_Professional.objects.get(professional_id=ord.professional_id.professional_id)
        notification = Notification.objects.create(
            notification= f"Hey {professional.full_name}, Thankyou for Solving request id {ord.order_id} requested by {homeowner.full_name}.",
            classification="Professional",
            professional_id =  professional
            )
        notification.save()
        notifications = Notification.objects.create(
                    notification= f"Hey {homeowner.full_name}, Your Problem has been solved by {professional.full_name}.",
                    classification="HomeOwner",
                    homeowner_id = homeowner
                    )
        notifications.save()
        notificationss = Notification.objects.create(
            notification= f"{homeowner.full_name}, problem has been solved by {professional.full_name} having booking id {ord.order_id}",
            classification="Admin",
            )
        notificationss.save()
    else:
        instance.status = 'book'
        instance.message = message
        instance.totaltimehour = totalhour
        instance.save()
    previous_url = request.META.get('HTTP_REFERER')
    return redirect(previous_url)

@login_required(login_url="hsignin")
def notification(request):
    username = request.user.username
    if username:
            homeowner_id = Account_HomeOwner.objects.get(username=username)
            print(homeowner_id)
    msg = Notification.objects.filter(Q(classification="All") | Q(classification="All_HomeOwner") | Q(classification="HomeOwner", homeowner_id=homeowner_id)).order_by('-time')
    return render(request, "homeowners/notification.html", {'msg':msg})

@login_required(login_url="hsignin")
def profile(request):
    username = request.user.username
    hprofile = Account_HomeOwner.objects.get(username=username)
    mainhprofile = User.objects.get(username=username)
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        address = request.POST.get('address')
        photo = request.FILES.get('photo')
        username = request.POST.get('username')

        if User.objects.filter(username=username).exclude(username=request.user.username).exists():
            messages.info(request, "Username already exists")
            return redirect('profile')
        
        if User.objects.filter(email=email, is_professional=True).exclude(email=request.user.email).exists():
            messages.info(request, "Email already exists")
            return redirect('profile')
        
        # Retrieve the user's Account_HomeOwner object and update its fields
        mainhprofile.username = username
        mainhprofile.email = email
        mainhprofile.save()
        
        hprofile.full_name = full_name
        hprofile.email = email
        hprofile.number = number
        hprofile.address = address
        if photo:
            hprofile.photo = photo
        hprofile.username = username
        hprofile.save() 
        messages.success(request, "Profile updated successfully")
    
    return render(request, "homeowners/profile.html",{'hprofile':hprofile})

@login_required(login_url="hsignin")
def changepassword(request):
    username = request.user.username
    hprofile = Account_HomeOwner.objects.get(username=username)
    mainhprofile = User.objects.get(username=username)
    if request.method == 'POST':
        password = request.POST.get('password')

        # Retrieve the user's Account_HomeOwner object and update its fields
        mainhprofile.password = make_password(password)
        mainhprofile.save()
        hprofile.password = make_password(password)
        hprofile.save() 
        messages.success(request, "Password updated successfully")
    
    return render(request, "homeowners/changepassword.html",{'hprofile':hprofile})

@login_required(login_url="hsignin")
def viewprofile(request):
    username = request.user.username
    hprofile = Account_HomeOwner.objects.get(username=username)
    return render(request, "homeowners/viewprofile.html",{'hprofile':hprofile})


@login_required(login_url="hsignin")
def bookings(request):
    username = request.user.username
    alldata = Account_HomeOwner.objects.get(username=username)
    ord = Order.objects.filter(homeowner_id=alldata.homeowner_id).order_by('-date')
    return render(request, "homeowners/bookings.html",{'ord':ord})

@login_required(login_url="hsignin")
def bookingdetails(request,od):
    ord = Order.objects.get(order_id=od)
    sk_service = ord.professional_id.subservice
    servicedata = All_Service.objects.get(subservice=sk_service)
    if ord.status == 'cancel':
        status = 'Cancel'
    elif ord.status == 'solve':
        status = 'Solve'
    else:
        status = 'Book'
        
    #cash Payment
    if request.method == 'POST':
        amount = int(request.POST['amount'])
        if amount:
            orderid = request.POST['orderid']

        try:
            order = Order.objects.get(order_id=orderid)
        except Order.DoesNotExist:
            # Handle the case where the order ID doesn't exist
            return HttpResponse("TryAgain")

        order.payment_amount = amount
        order.payment_date = datetime.now()
        order.payment_method = "Cash"
        order.save()
        return redirect(request.path)
    return render(request, "homeowners/bookingdetails.html",{'ord':ord, 'status':status, 'servicedata': servicedata})

@login_required(login_url="psignin")
def requestdetails(request,rd):
    ord = Order.objects.get(order_id=rd)
    if ord.status == 'cancel':
        status = 'Cancel'
    elif ord.status == 'solve':
        status = 'Solve'
    else:
        status = 'Book'
    return render(request, "professionals/requestdetails.html",{'ord':ord, 'status':status})

@login_required(login_url="psignin")
def request(request):
    username = request.user.username
    ord = Order.objects.all()
    alldata = Account_Professional.objects.get(username=username)
    ord = Order.objects.filter(professional_id=alldata.professional_id).order_by('-date')
    return render(request, "professionals/request.html",{'ord':ord})

@login_required(login_url="psignin")
def professionalprofile(request):
    username = request.user.username
    po = Account_Professional.objects.get(username=username)
    mainpprofile = User.objects.get(username=username)
    if request.method == 'POST':
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        address = request.POST.get('address')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        exprience = request.POST.get('exprience')
        rateperhour = request.POST.get('rateperhour')
        photo = request.FILES.get('photo')
        desc = request.POST.get('desc')
        
        if User.objects.filter(username=username).exclude(username=request.user.username).exists():
            messages.info(request, "Username already exists")
            return redirect('professionalprofile')
               
        if User.objects.filter(email=email, is_professional=True).exclude(email=request.user.email).exists():
            messages.info(request, "Email already exists")
            return redirect('professionalprofile')
        
        # Retrieve the user's Account_HomeOwner object and update its fields
        mainpprofile.username = username
        mainpprofile.email = email
        mainpprofile.save()
        
        po.full_name = full_name
        po.email = email
        po.number = number
        po.username = username
        po.address = address
        po.age = age
        po.gender = gender
        po.exprience = exprience
        po.rateperhour = rateperhour
        if photo:
            po.photo = photo
        po.desc = desc
        po.save() 
        messages.success(request, "Profile updated successfully")
    return render(request, "professionals/professionalprofile.html",{'po':po})

@login_required(login_url="psignin")
def professionalchangepassword(request):
    username = request.user.username
    po = Account_Professional.objects.get(username=username)
    mainpprofile = User.objects.get(username=username)
    if request.method == 'POST':
        password = request.POST.get('password')

        # Retrieve the user's Account_HomeOwner object and update its fields
        mainpprofile.password = make_password(password)
        mainpprofile.save()
        po.password = make_password(password)
        po.save() 
        messages.success(request, "Password updated successfully")
    return render(request, "professionals/professionalchangepassword.html",{'po':po})

@login_required(login_url="psignin")
def professionalviewprofile(request):
    username = request.user.username
    po = Account_Professional.objects.get(username=username)
    return render(request, "professionals/professionalviewprofile.html",{'po':po})
  

@login_required(login_url="psignin")
def professionalnotification(request):
    username = request.user.username
    print(username)
    if username:
            professional_id = Account_Professional.objects.get(username=username)        
    msg = Notification.objects.filter(Q(classification="All") | Q(classification="All_Professional") | Q(classification="Professional", professional_id=professional_id)).order_by('-time')
    return render(request, "professionals/professionalnotification.html",{'msg':msg})


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
        photo = request.FILES.get('photo')
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
    msg = Notification.objects.filter(Q(classification="All") | Q(classification="Admin")).order_by('-time')
    return render(request, "admin/adminnotification.html",{'msg':msg})

@login_required(login_url="adminsignin")
def notify(request):
    classificationss = [choice[1] for choice in Notification.CLASSIFICATION_CHOICES]
    print(classificationss)
    homeownerss = Notification.objects.all().distinct('homeowner_id')
    professionalss = Notification.objects.all().distinct('professional_id')
    
    if request.method == "POST":
        notification = request.POST.get('notification')
        classification = request.POST.get('classification')
        homeowner_username = request.POST.get('homeowner')
        professional_username = request.POST.get('professional')
        
        homeowner = None
        if homeowner_username:
            homeowner = Account_HomeOwner.objects.get(username=homeowner_username)
            print(homeowner)
        
        professional = None
        if professional_username:
            professional = Account_Professional.objects.get(username=professional_username)
            print(professional)

        # Create a new notification instance
        notification = Notification.objects.create(
            notification=notification,
            classification=classification,
            homeowner_id=homeowner,
            professional_id=professional,
        )
        messages.info(request, 'Notification created successfully!')
        return redirect('notify')
    
    return render(request, "admin/notify.html", locals())





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
    instance = get_object_or_404(Account_Professional, pk=professional_id)
    ins = get_object_or_404(User, pk=instance.user.pk)
    instance.status = not instance.status
    ins.is_active = not ins.is_active
    instance.save()
    ins.save()
    previous_url = request.META.get('HTTP_REFERER')
    return redirect(previous_url)

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
        messages.info(request, 'Please Send Again.')
        
    return render(request, 'adminservicedetail', {'serv': serv})


@login_required(login_url=["hsignin", "psignin"])
def usermessage(request):
    if request.method == "POST":
        message = request.POST.get('message')
        print(message)
        usernamea = ""
        usernameb = ""
        try:
            usernamea = Account_HomeOwner.objects.get(username=request.user.username)
        except Account_HomeOwner.DoesNotExist:
            try:
                usernameb = Account_Professional.objects.get(username=request.user.username)
            except Account_Professional.DoesNotExist:
                django_messages.info(request, 'Please Send Again.')
                return redirect(request.META['HTTP_REFERER'])
        
        message_instance = Message(homeowner_id=usernamea if usernamea else None, professional_id=usernameb if usernameb else None, message=message)
        message_instance.save() 
        django_messages.info(request, 'Thank-you for your valuable feedback.')
  
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url=["hsignin", "psignin"])
def rate_professional(request, prof_id, ord_id):
    ords = Order.objects.get(order_id=ord_id)
    print(prof_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        if ords.ratingcheck==False:
            if rating:
                try:
                    prof = Account_Professional.objects.get(professional_id=prof_id)
                    # check if the user has already rated the professional
                    if prof.ratings==0:
                        prof.ratings = rating
                        prof.num_ratings += 1
                        prof.save()
                        ords.ratingcheck = True
                        ords.save()
                        messages.success(request, 'Your rating has been submitted successfully.', extra_tags='rating')
                    else:
                        prof.ratings = (prof.ratings + rating)/2
                        prof.num_ratings += 1 
                        prof.save()
                        ords.ratingcheck = True
                        ords.save()
                        messages.success(request, 'Your rating has been submitted successfully.', extra_tags='rating')
                    prof.save()
                    username = request.user.username
                    if username:
                        homeowner = Account_HomeOwner.objects.get(username=username)   
                    notification = Notification.objects.create(
                        notification= f"Hey {prof.full_name}, Yo have got rating {rating} by {homeowner.full_name}.",
                        classification="Professional",
                        professional_id = prof
                        )
                    notification.save()
                    notifications = Notification.objects.create(
                        notification= f"Hey {homeowner.full_name}, Thankyou for rating {rating} to {prof.full_name}.",
                        classification="HomeOwner",
                        homeowner_id = homeowner
                        )
                    notifications.save()
                    notificationss = Notification.objects.create(
                        notification= f"{homeowner.full_name}, gives the rating {rating} to {prof.full_name}",
                        classification="Admin",
                        )
                    notificationss.save()  
                    return redirect('bookingdetails', pk=ord_id)  # add this line
                except Account_Professional.DoesNotExist:
                    previous_url = request.META.get('HTTP_REFERER')
                    return redirect(previous_url)
            else:
                messages.error(request, 'Please select a rating.', extra_tags='rating')
                previous_url = request.META.get('HTTP_REFERER')
                return redirect(previous_url)

        else:
            messages.error(request, 'Sorry, You already give rating the professionals', extra_tags='rating')
            previous_url = request.META.get('HTTP_REFERER')
            return redirect(previous_url)
            
    else:
        previous_url = request.META.get('HTTP_REFERER')
        return redirect(previous_url)


def entry_not_found(request, exception='1', template_name='404.html'):
    return render(request, template_name)



    
def hforgetpassword(request):
    return render(request, "homeowners/hforgetpassword.html")

import random
def send_otp(request):
    messages.error(request, '') 
    otp = random.randint(11111,99999)
    username = request.POST.get('username')
    user_username = Account_HomeOwner.objects.filter(username=username)
    if user_username:
        getuser = Account_HomeOwner.objects.get(username=username)
        email=getuser.email
        user = Account_HomeOwner.objects.get(email=email)
        user.otp = otp
        user.save()
        print(email)
        request.session['email'] = email
        html_message = "As part of our commitment to ensuring the security of your account, we have implemented a One-Time Password (OTP) feature. This feature provides an additional layer of protection to your account by requiring a unique code that is sent to your registered email address. To access your account, please enter the following OTP:  : - "+"" + str(otp)
        subject = "OTP Conformation"
        email_from = settings.EMAIL_HOST_USER
        email_to= [email]
        message = EmailMessage(subject, html_message, email_from, email_to)
        message.send()
        messages.success(request, 'One Time Password send to your Email')
        return redirect('enter_otp')
    else:
        messages.error(request, 'Please Enter Correct Username') 
    return render(request, "homeowners/hforgetpassword.html")

def enter_otp(request):
    messages.error(request, '') 
    if request.session.has_key('email'):
        email = request.session['email']
        user = Account_HomeOwner.objects.filter(email=email)
        for u in user:
            user_otp = u.otp
        if request.method =="POST":
            otp = request.POST.get('otp')
            if not otp:
                messages.error(request, 'OTP Code is required') 
            elif not user_otp == otp:
                messages.error(request, 'OTP Code is not matched') 
            elif otp==user_otp:
                return redirect("password_reset")
        return render(request,'homeowners/enter_otp.html')
    return render(request, "homeowners/hforgetpassword.html")



def password_reset(request):
    messages.error(request, '')
    if request.session.has_key('email'):
        email = request.session['email']
        user = Account_HomeOwner.objects.get(email=email)
        username = user.username
        mainuser = User.objects.get(username=username)
        
        if request.method == "POST":
            newpassword = request.POST.get('newpassword')
            conformnewpassword = request.POST.get('conformnewpassword')

            if not newpassword:
                messages.error(request, 'Enter New Password')
            elif not conformnewpassword:
                messages.error(request, 'Enter New Conform Password')
            elif newpassword != conformnewpassword:
                messages.error(request, 'Password Not Match')
            else:
                # Generate new password hash
                new_password_hash = make_password(newpassword)

                # Compare new password hash with existing password hash
                if check_password(newpassword, user.password):
                    messages.error(request, 'The Password Already Exists. Please try a new password.')
                else:
                    # Update password for both user and mainuser objects
                    user.password = new_password_hash
                    user.save()
                    mainuser.password = new_password_hash
                    mainuser.save()
                    messages.success(request, 'Password Changed Successfully')
                    return redirect("hsignin")
    return render(request, "homeowners/password_reset.html")

#password reset of professionals
def pforgetpassword(request):
    return render(request, "professionals/pforgetpassword.html")


def psend_otp(request):
    messages.error(request, '') 
    otp = random.randint(11111,99999)
    username = request.POST.get('username')
    user_username = Account_Professional.objects.filter(username=username)
    if user_username:
        getuser = Account_Professional.objects.get(username=username)
        email=getuser.email
        user = Account_Professional.objects.get(email=email)
        user.otp = otp
        user.save()
        print(email)
        request.session['email'] = email
        html_message = "As part of our commitment to ensuring the security of your account, we have implemented a One-Time Password (OTP) feature. This feature provides an additional layer of protection to your account by requiring a unique code that is sent to your registered email address. To access your account, please enter the following OTP:  : - "+"" + str(otp)
        subject = "OTP Conformation"
        email_from = settings.EMAIL_HOST_USER
        email_to= [email]
        message = EmailMessage(subject, html_message, email_from, email_to)
        message.send()
        messages.success(request, 'One Time Password send to your Email')
        return redirect('penter_otp')
    else:
        messages.error(request, 'Please Enter Correct Username') 
    return render(request, "professionals/pforgetpassword.html")

def penter_otp(request):
    messages.error(request, '') 
    if request.session.has_key('email'):
        email = request.session['email']
        user = Account_Professional.objects.filter(email=email)
        for u in user:
            user_otp = u.otp
        if request.method =="POST":
            otp = request.POST.get('otp')
            if not otp:
                messages.error(request, 'OTP Code is required') 
            elif not user_otp == otp:
                messages.error(request, 'OTP Code is not matched') 
            elif otp==user_otp:
                return redirect("ppassword_reset")
        return render(request,'professionals/penter_otp.html')
    return render(request, "professionals/pforgetpassword.html")

def ppassword_reset(request):
    messages.error(request, '')
    if request.session.has_key('email'):
        email = request.session['email']
        user = Account_Professional.objects.get(email=email)
        username = user.username
        mainuser = User.objects.get(username=username)
        
        if request.method == "POST":
            newpassword = request.POST.get('newpassword')
            conformnewpassword = request.POST.get('conformnewpassword')

            if not newpassword:
                messages.error(request, 'Enter New Password')
            elif not conformnewpassword:
                messages.error(request, 'Enter New Conform Password')
            elif newpassword != conformnewpassword:
                messages.error(request, 'Password Not Match')
            else:
                # Generate new password hash
                new_password_hash = make_password(newpassword)

                # Compare new password hash with existing password hash
                if check_password(newpassword, user.password):
                    messages.error(request, 'The Password Already Exists. Please try a new password.')
                else:
                    # Update password for both user and mainuser objects
                    user.password = new_password_hash
                    user.save()
                    mainuser.password = new_password_hash
                    mainuser.save()
                    messages.success(request, 'Password Changed Successfully')
                    return redirect("psignin")
    return render(request, "professionals/ppassword_reset.html")

                
                
                
    











