from django.shortcuts import render, redirect
from django.contrib import messages
from account.models import User
from django.contrib.auth import authenticate, login
from account.models import Account_HomeOwner, Account_Professional
from account.models import All_Service
from django.contrib.auth import logout as auth_logout
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from account.models import Notification

#login function for Homeowners
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from mysite.urls import redirect_to_service

#register Function for HomeOwner   

def hsignin(request):
    if redirect_to_service(request)['Location'] == '/request':
        return redirect('request')
    if redirect_to_service(request)['Location'] == '/service':
        return redirect('service')
    if redirect_to_service(request)['Location'] == '/adminhomepage':
        return redirect('adminhomepage')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_homeowner:
            login(request, user)
            if request.user.is_authenticated or not request.session.get_expiry_date():
                # Redirect to the service page if user is already logged in or session has not expired
                return redirect('service')
            else:
                # Redirect to the dashboard page if user is not logged in or session has expired
                return redirect('hsignin')
        else:
            messages.info(request, 'Invalid Login Credentials')
            return redirect('hsignin')
    else:
        return render(request, "homeowners/hsignin.html")
    
    
    

def hsignup(request):
    if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        number = request.POST['number']
        address = request.POST['address']
        photo = request.FILES.get('photo')
        homepassword1 = request.POST['homepassword1']
        password = request.POST['password']
        username = request.POST['username']

        if password != homepassword1:
            messages.info(request, "Passwords do not match")
            return redirect('hsignup')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already exists")
            return redirect('hsignup')
        
        if User.objects.filter(email=email, is_homeowner=True).exists():
            messages.info(request, "Email already exists")
            return redirect('hsignup')

        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password, is_homeowner=True)
            data = Account_HomeOwner.objects.create(
                full_name=full_name,
                email=email,
                number=number,
                address=address,
                photo=photo,
                password=password,
                username=username,
                user=user,
            )
            notification = Notification.objects.create(
                notification="Well Come to SewaGhar",
                classification="HomeOwner",
                homeowner_id=data
            )
            notifications = Notification.objects.create(
                notification="{full_name} Create the account as a HomeOwner",
                classification="Admin",
            )
            notification.save()
            notifications.save()
            messages.info(request, "User created successfully")
            return redirect('hsignin')
        except Exception as e:
            messages.info(request, str(e))
            return redirect('hsignup')
    return render(request, "homeowners/hsignup.html")

 
def hforgetpassword(request):
    return render(request, "homeowners/hforgetpassword.html")
         


def psignin(request):
    if redirect_to_service(request)['Location'] == '/request':
        return redirect('request')
    if redirect_to_service(request)['Location'] == '/service':
        return redirect('service')
    if redirect_to_service(request)['Location'] == '/adminhomepage':
        return redirect('adminhomepage')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:  # check if user is not None before checking attributes
            if user.is_active:
                if user.is_professional:
                    login(request, user)
                    return redirect('request')
                else: 
                    messages.info(request, 'Login through HomeOwner')
                    return redirect('psignin')
            else: 
                messages.info(request, 'You are going to activated or deactivated by admin')
                return redirect('psignin')
        else:  
            messages.info(request, 'Invalid Login Credentials')
            return redirect('psignin')
    else:  # if request method is not POST, render the 'psignin' page
        return render(request, "professionals/psignin.html")
    
def psignup(request):
     service_id = request.GET.get('service',None)
     if service_id:
         try:
             ss = All_Service.objects.get(service_id=service_id) 
             service = ss.service 
             if service:
                 subservice = All_Service.objects.filter(service=service)
         except All_Service.DoesNotExist:
             # Handle case where no matching All_Service object was found
             pass
     else:
         # Handle case where no service_id was provided in the GET request
         pass
     service = All_Service.objects.all().distinct('service')
     if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        number = request.POST['number']
        address = request.POST['address']
        age = request.POST['age']
        gender = request.POST['gender']
        service = request.POST['service']
        service = All_Service.objects.get(service_id=service) 
        service = service.service 
        subservice = request.POST['subservice']
        exprience = request.POST['exprience']
        rateperhour = request.POST['rate']
        citizenship = request.FILES.get('citizenship')
        citizenships = request.FILES.get('citizenships')
        photo = request.FILES.get('photo')
        desc = request.POST['desc']
        password1 = request.POST['password1']
        password = request.POST['password']
        username = request.POST['username']
        print(service)
        
        if password != password1:
            messages.info(request, "Passwords do not match")
            return redirect('psignup')
        
                # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already exists")
            return redirect('psignup')
        
        
        if User.objects.filter(email=email, is_professional=True).exists():
            messages.info(request, "Email already exists")
            return redirect('psignup')
    
        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password, is_professional=True, is_active=False)
            data = Account_Professional.objects.create(
            full_name = full_name,
                    email = email,
                    number = number,
                    address = address,
                    age = age,
                    gender = gender,
                    service = service,
                    subservice =subservice,
                    exprience = exprience,
                    rateperhour = rateperhour,
                    photo = photo,
                    citizenship = citizenship,
                    citizenships = citizenships,
                    password = password,
                    username = username,
                    desc = desc,
                    user = user
            )
            notification = Notification.objects.create(
                notification="Well Come to SewaGhar",
                classification="Professional",
                professional_id = data 
            )
            notifications = Notification.objects.create(
                notification="{full_name} Create the account as a Professional for service {service}-{subservice}",
                classification="Admin",
            )
            
            user.save()
            data.save()
            notification.save()
            notifications.save()
            messages.info(request, "User created successfully")
            return redirect('psignin')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('psignup')
     else:
         return render(request, "professionals/psignup.html",locals())


 
def user_logout(request):
    auth_logout(request)
    return redirect("/")


def adminsignin(request):
    if redirect_to_service(request)['Location'] == '/request':
        return redirect('request')
    if redirect_to_service(request)['Location'] == '/service':
        return redirect('service')
    if redirect_to_service(request)['Location'] == '/adminhomepage':
        return redirect('adminhomepage')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_admin:
            login(request, user)
            if request.user.is_authenticated or not request.session.get_expiry_date():
                return redirect('adminhomepage')
            else:
                # Redirect to the dashboard page if user is not logged in or session has expired
                return redirect('adminsignin')
        else:
            messages.info(request, 'Invalid Login Credentials')
            return redirect('adminsignin')
    else:
        return render(request, "admin/adminsignin.html")




def index(request):
    return render(request, 'index.html')

