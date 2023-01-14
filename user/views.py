from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login

# Create your views here.
def hsignin(request):
     if request.method=='POST':
         email = request.POST['email']
         password = request.POST['password']   
         user = User.objects.get(email=email)  
         username=user.username
         user = authenticate(request, username=username, password=password)
         print(user)
         
         if user is not None:
             login(request,user)
             return redirect('service')
         else:
             messages.info(request,"Wrong email or password")
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
        homepassword2 = request.POST['homepassword2']
        username = request.POST['full_name']
        
        if homepassword1==homepassword2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'Sorry! Email Already Exists')
                return redirect('hsignup')
            else:
                user = User.objects.create_user(password=homepassword1,username=username, email=email)
                user.save()
                messages.info(request,'Congratulations! Account Created')
                return redirect('hsignin')
        else:
            messages.info(request,'Sorry! Password not match')
            return redirect('hsignup')
     else:
         return render(request, "homeowners/hsignup.html")

def psignin(request):
    return render(request, "professionals/psignin.html")


def psignup(request):
    return render(request, "professionals/psignup.html")    
    
def logout(request):
    auth.logout(request)
    return redirect("/")


