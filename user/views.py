from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login
from user.models import Account_HomeOwner
from user.models import Account_Professional



# Create your views here.
def hsignin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']   
        user = User.objects.get(username=username)  
        username=user.username
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('service')
        else:
            messages.info(request,'Invalid Login Credentials')
            return redirect('hsignin')
    else:
        return render(request, "homeowners/hsignin.html")
    
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
        
        if password==homepassword1:
            if Account_HomeOwner.objects.filter(email=email).exists():
                messages.info(request,'Sorry! Email Already Exists')
                return redirect('hsignup')
            elif Account_HomeOwner.objects.filter(username=username).exists():
                messages.info(request,'Sorry! Username Already Exists')
                return redirect('hsignup')
            else:
                user = Account_HomeOwner(
                    full_name = full_name,
                    email = email,
                    number = number,
                    address = address,
                    photo = photo,
                    password = password,
                    username = username
                    )       
                user.save()
                messages.info(request,'Congratulations! Account Created')
                return redirect('hsignin')
        else:
            messages.info(request,'Sorry! Password not match')
            return redirect('hsignup')
     else:
         return render(request, "homeowners/hsignup.html")
     
def psignin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.get(username=username)  
        username=user.username
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('request')
        else:
            messages.info(request,'Invalid Login Credentials')
            return redirect('psignin')
    else:
        return render(request, "professionals/psignin.html")
    
def psignup(request):
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
        
        if password==password1:
            if Account_Professional.objects.filter(email=email).exists():
                messages.info(request,'Sorry! Email Already Exists')
                return redirect('psignup')
            elif Account_Professional.objects.filter(username=username).exists():
                messages.info(request,'Sorry! Username Already Exists')
                return redirect('psignup')
            else:
                user = Account_Professional(
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
                user.save()
                messages.info(request,'Congratulations! Account Created')
                return redirect('psignin')
        else:
            messages.info(request,'Sorry! Password not match')
            return redirect('psignup')
     else:
         return render(request, "professionals/psignup.html")
     
def logout(request):
    auth.logout(request)
    return redirect("/")

def adminsignin(request):  
     if request.method=='POST':
         email = request.POST['email']
         password = request.POST['password']   
         user = User.objects.get(email=email)  
         username=user.username
         user = authenticate(request, username=username, password=password)
         
         print(user)

         if user is not None:
             login(request,user)
             return redirect('adminhomepage')
         
         else:
             messages.info(request,"Wrong email or password")
             return redirect('adminsignin')
         
     else:
        return render(request, "admin/adminsignin.html")  