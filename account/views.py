from django.shortcuts import render, redirect
from django.contrib import messages
from account.models import User
from django.contrib.auth import authenticate, login
from account.models import Account_HomeOwner, Account_Professional
from account.models import All_Service

#login function for Homeowners
def hsignin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_homeowner:
            login(request, user)
            return redirect('service')
        else:
            messages.info(request, 'Invalid Login Credentials')
            return redirect('hsignin')
    else:
        return render(request, "homeowners/hsignin.html")
    
#register Function for HomeOwner   
def hsignup(request):
     if request.method == 'POST':
        full_name = request.POST['full_name']
        email = request.POST['email']
        number = request.POST['number']
        address = request.POST['address']
        photo = request.POST['photo']
        homepassword1 = request.POST['homepassword1']
        password = request.POST['password']
        username = request.POST['username']
       
        
        if password != homepassword1:
            messages.error(request, "Passwords do not match")
            return redirect('hsignup')
    
        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password, is_homeowner=True)
            data = Account_HomeOwner(
            full_name = full_name,
            email = email,
            number = number,
            address = address,
            photo = photo ,
            password = password,
            username = username,
            )
            data.save()
            # user.first_name = full_name
            user.save()
            messages.success(request, "User created successfully")
            return redirect('hsignin')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('hsignup')
     return render(request, "homeowners/hsignup.html")
     
     
def psignin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_professional:
            login(request, user)
            return redirect('request')
        else:
            messages.info(request, 'Invalid Login Credentials')
            return redirect('psignin')
    else:
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
        subservice = request.POST['subservice']
        exprience = request.POST['exprience']
        citizenship = request.POST['citizenship']
        photo = request.POST['photo']
        password1 = request.POST['password1']
        password = request.POST['password']
        username = request.POST['username']
         
        
        if password != password1:
            messages.error(request, "Passwords do not match")
            return redirect('psignup')
    
        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password, is_professional=True)
            data = Account_Professional(
            full_name = full_name,
                    email = email,
                    number = number,
                    address = address,
                    age = age,
                    gender = gender,
                    service = service,
                    subservice =subservice,
                    exprience = exprience,
                    photo = photo,
                    citizenship = citizenship,
                    password = password,
                    username = username
            )
            data.save()
            user.save()
            messages.success(request, "User created successfully")
            return redirect('psignin')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('psignup')
     else:
         return render(request, "professionals/psignup.html",locals())
 
def logout(request):
    User.auth.logout(request)
    return redirect("/") 

def adminsignin(request):  
  if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_admin:
            login(request, user)
            return redirect('adminhomepage')
        else:
             messages.info(request,"Wrong email or password")
             return redirect('adminsignin')
  else:
    return render(request, "admin/adminsignin.html")
def index(request):
    return render(request, 'index.html')

