from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from account.models import Account_HomeOwner
from account.models import Account_Professional
from account.models import Order
from account.models import All_Service
from account.models import Service_List
from account.models import Notification
from account.models import Message
from account.models import Blog
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
from django.views.decorators.csrf import csrf_exempt
from account.models import SiteConfig
from account.models import ContactMessage
import json
import calendar
import requests
import random



# Create your views here.

def slot_conflict(professional, selected_datetime):
    """True when the professional has an active booking within 1 hour of the slot."""
    for order in Order.objects.filter(professional_id=professional, status__in=['book', 'accept']):
        existing = datetime.combine(order.date, order.time)
        if abs((selected_datetime - existing).total_seconds()) < 3600:
            return True
    return False


def order_payable(order):
    """Amount due for a solved order: fixed quote wins, else hours x agreed rate."""
    if order.quoted_amount:
        return round(order.quoted_amount, 2)
    try:
        rate = float(order.offered_rate or order.professional_id.rateperhour or 0)
    except (TypeError, ValueError):
        rate = 0
    return round((order.totaltimehour or 0) * rate, 2)


def home(request):
    return render(request, "home.html")

def blog(request):
    blog = Blog.objects.all()
    return render(request, "blog.html",{"blog":blog})

def aboutus(request):
    return render(request, "aboutus.html")

def privacypolicy(request):
    return render(request, "privacypolicy.html")

def termsandcondition(request):
    return render(request, "termsandcondition.html")



@login_required(login_url="hsignin")
def service(request):
    # import ipdb;ipdb.set_trace()
    if request.user.is_homeowner is True:
        query = request.GET.get('q')
        # One entry per service name. values().distinct() is portable SQL
        # (plain SELECT DISTINCT) unlike the PostgreSQL-only distinct('field').
        if query:
            serv = All_Service.objects.filter(service__icontains=query).values('service').distinct().order_by('service')
        else:
            serv = All_Service.objects.values('service').distinct().order_by('service')

        return render(request, "homeowners/service.html", {'serv': serv, 'query': query})
    else:
        return redirect('404')


@login_required(login_url="hsignin")
def subservice(request,sk):
    if request.user.is_homeowner is True:
        servs = All_Service.objects.filter(service=sk)
        s = sk
        servs = {'servs': servs}
        so = {'s': s}
        context = {**servs, **so}
        return render(request, "homeowners/subservice.html",context)
    else:
        return redirect('404')
            

@login_required(login_url="hsignin")
def servicetime(request,bk): 
    if request.user.is_homeowner is True:
        sk = Account_Professional.objects.get(professional_id=bk)
        sk_service = sk.subservice
        servicedata = All_Service.objects.get(subservice=sk_service)
        servs = Account_Professional.objects.filter(professional_id=bk)
        serdis = All_Service.objects.filter(subservice__in=servs.values('subservice')).values('service_id')
        print(serdis.values("service"))
        s = bk  
        
        current_datetime = datetime.now()
        offered_rate = None
        if request.method == 'POST':
            selected_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d').date()
            selected_time = datetime.strptime(request.POST.get('time'), '%H:%M').time()

            error_message = None
            if selected_date < current_datetime.date():
                error_message = "Selected date has already passed. Please pick a date from today onwards."
            elif (selected_date - current_datetime.date()).days > 30:
                error_message = "Bookings can be made at most 30 days in advance."
            elif selected_date == current_datetime.date() and selected_time < current_datetime.time():
                error_message = "Selected time cannot be before the current time."
            elif slot_conflict(sk, datetime.combine(selected_date, selected_time)):
                error_message = f"{sk.full_name} is not available at that time - another booking is within 1 hour. Please take another slot."

            # price offer must stay within 50%-150% of the listed rate
            try:
                base_rate = float(sk.rateperhour or 0)
            except (TypeError, ValueError):
                base_rate = 0
            raw_offer = request.POST.get('offered_rate')
            if raw_offer:
                try:
                    offered_rate = float(raw_offer)
                except ValueError:
                    offered_rate = None
            if error_message is None and offered_rate is not None and base_rate > 0:
                if not (base_rate * 0.8 <= offered_rate <= base_rate * 1.5):
                    error_message = f"Your price offer must stay between Rs. {base_rate * 0.8:g} and Rs. {base_rate * 1.5:g} per hour."

            if error_message:
                return render(request, 'homeowners/servicetime.html', {'error_message': error_message, 's': s, 'sk': sk, 'servicedata': servicedata})
        
        
        if request.method =="POST":
            date = request.POST.get('date')
            time = request.POST.get('time')
            number = request.POST.get('number')
            houseno = request.POST.get('houseno')
            address = request.POST.get('address')
            googlemap = request.POST.get('gmap')
            
            
            
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
                googlemap = googlemap,
                professional_id = servs[0],
                homeowner_id = homeowner,
                offered_rate = offered_rate,
                jobdesc = (request.POST.get('jobdesc') or '').strip() or None
            )
            serv.save()
            notification = Notification.objects.create(
                    notification= f"New booking request from {homeowner.full_name}.",
                    classification="Professional",
                    professional_id = professional 
                )
            notification.save()
            notifications = Notification.objects.create(
                    notification= f"You booked {professional.full_name}. Waiting for them to accept.",
                    classification="HomeOwner",
                    homeowner_id = homeowner 
                )
            notifications.save()
            notificationss = Notification.objects.create(
                    notification= f"{homeowner.full_name} booked {professional.full_name} for {servicedata.service} - {servicedata.subservice}.",
                    classification="Admin",
                )
            notificationss.save()
            order_id = serv.order_id  
            messages.success(request, 'Service Booked Sucessfully', extra_tags='loginsucess')
            return redirect('unbook', prof_id=s, order_id=order_id)
        
        serdis = {'serdis':serdis}
        servs = {'servs': servs} 
        servicedata = {'servicedata': servicedata} 
        so = {'s': s}
        sk = {'sk':sk}
        context = {**servs, **so, **serdis, **servicedata, **sk}
        return render(request, "homeowners/servicetime.html",context)
    else:
        return redirect('404')

    
@login_required(login_url="hsignin")
def servicemanlist(request, slk):
    if request.user.is_homeowner is True:
        servicedata = All_Service.objects.get(subservice=slk)
        servs = Account_Professional.objects.filter(subservice=slk, online=True, status=True).order_by('-ratings')
        context = {'servs': servs, 'servicedata': servicedata}
        return render(request, "homeowners/servicemanlist.html", context)
    else:
        return redirect('404')



@login_required(login_url="hsignin")
def book(request,sml):
    if request.user.is_homeowner is True:
        sk = Account_Professional.objects.get(professional_id=sml)
        sk_service = sk.subservice
        servicedata = All_Service.objects.get(subservice=sk_service)
        return render(request, "homeowners/book.html",{'sk':sk, 'servicedata':servicedata})
    else:
        return redirect('404')

@login_required(login_url="hsignin")
def unbook(request, prof_id, order_id):
    if request.user.is_homeowner is True:
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
        return render(request, "homeowners/unbook.html",{'sk':sk, 'ord':ord, 'status':status, 'servicedata':servicedata, 'payable': order_payable(ord)})
    else:
        return redirect('404')

@login_required(login_url="hsignin")
def activates(request, order_id):
        instance = get_object_or_404(Order, order_id=order_id)
        status = request.POST.get('status')
        message = request.POST.get('messagess')
        # An absent or empty field must become None: totaltimehour is a
        # FloatField and saving '' would raise a 500.
        totalhour = request.POST.get('totalhour') or None
        
        if status == 'cancel':
            instance.status = 'cancel'
            instance.message = message
            instance.totaltimehour = totalhour
            instance.save()
            ord = Order.objects.get(order_id=order_id)
            homeowner = Account_HomeOwner.objects.get(homeowner_id=ord.homeowner_id.homeowner_id)
            professional = Account_Professional.objects.get(professional_id=ord.professional_id.professional_id)
            notification = Notification.objects.create(
                notification= f"Request #{ord.order_id} was cancelled by {homeowner.full_name}.",
                classification="Professional",
                professional_id =  professional
                )
            notification.save()
            notifications = Notification.objects.create(
                notification= f"You cancelled booking #{ord.order_id}.",
                classification="HomeOwner",
                homeowner_id = homeowner
                )
            notifications.save()
            notificationss = Notification.objects.create(
                notification= f"{homeowner.full_name} cancelled booking #{ord.order_id}.",
                classification="Admin",
                )
            notificationss.save()
            messages.success(request, 'Service Booking Cancelled', extra_tags='loginsucess')
        elif status == 'solve':
            instance.status = 'solve'
            instance.message = message
            instance.totaltimehour = totalhour
            # Fixed-price mode: the professional typed a total amount instead of hours.
            if request.POST.get('chargemode') == 'fixed':
                try:
                    instance.quoted_amount = float(request.POST.get('fixedamount'))
                except (TypeError, ValueError):
                    instance.quoted_amount = None
            instance.save()
            ord = Order.objects.get(order_id=order_id)
            homeowner = Account_HomeOwner.objects.get(homeowner_id=ord.homeowner_id.homeowner_id)
            professional = Account_Professional.objects.get(professional_id=ord.professional_id.professional_id)
            notification = Notification.objects.create(
                notification= f"Request #{ord.order_id} marked as solved. Great work!",
                classification="Professional",
                professional_id =  professional
                )
            notification.save()
            notifications = Notification.objects.create(
                        notification= f"Your problem was solved by {professional.full_name}. Please complete the payment.",
                        classification="HomeOwner",
                        homeowner_id = homeowner
                        )
            notifications.save()
            notificationss = Notification.objects.create(
                notification= f"{professional.full_name} solved booking #{ord.order_id} for {homeowner.full_name}.",
                classification="Admin",
                )
            notificationss.save()
            messages.success(request, 'Problem Solved', extra_tags='loginsucess')
            
        elif status == 'accept':
            instance.status = 'accept'
            instance.message = message
            instance.totaltimehour = totalhour
            instance.save()
            ord = Order.objects.get(order_id=order_id)
            homeowner = Account_HomeOwner.objects.get(homeowner_id=ord.homeowner_id.homeowner_id)
            professional = Account_Professional.objects.get(professional_id=ord.professional_id.professional_id)
            notification = Notification.objects.create(
                notification= f"You accepted request #{ord.order_id} from {homeowner.full_name}.",
                classification="Professional",
                professional_id =  professional
                )
            notification.save()
            notifications = Notification.objects.create(
                notification= f"Your booking #{ord.order_id} was accepted by {professional.full_name}.",
                classification="HomeOwner",
                homeowner_id = homeowner
                )
            notifications.save()
            notificationss = Notification.objects.create(
                notification= f"{professional.full_name} accepted booking #{ord.order_id} from {homeowner.full_name}.",
                classification="Admin",
                )
            notificationss.save()
            messages.success(request, 'Sucessfully Accepted', extra_tags='loginsucess')
            
        elif status == 'cancelbyprofessional':
            instance.status = 'cancelbyprofessional'
            instance.message = message
            instance.totaltimehour = totalhour
            instance.save()
            ord = Order.objects.get(order_id=order_id)
            homeowner = Account_HomeOwner.objects.get(homeowner_id=ord.homeowner_id.homeowner_id)
            professional = Account_Professional.objects.get(professional_id=ord.professional_id.professional_id)
            notification = Notification.objects.create(
                notification= f"You cancelled request #{ord.order_id}.",
                classification="Professional",
                professional_id =  professional
                )
            notification.save()
            notifications = Notification.objects.create(
                notification= f"Your booking #{ord.order_id} was cancelled by the professional.",
                classification="HomeOwner",
                homeowner_id = homeowner
                )
            notifications.save()
            notificationss = Notification.objects.create(
                notification= f"{professional.full_name} cancelled booking #{ord.order_id}.",
                classification="Admin",
                )
            notificationss.save()
            messages.success(request, 'Sucessfully Cancelled', extra_tags='loginsucess')
            
            
        else:
            instance.status = 'book'
            instance.message = message
            instance.totaltimehour = totalhour
            instance.save()
        previous_url = request.META.get('HTTP_REFERER')
        return redirect(previous_url)


@login_required(login_url="hsignin")
def notification(request):
    if request.user.is_homeowner is True:
        username = request.user.username
        if username:
                homeowner_id = Account_HomeOwner.objects.get(username=username)
        msg = Notification.objects.filter(Q(classification="All") | Q(classification="All_HomeOwner") | Q(classification="HomeOwner", homeowner_id=homeowner_id)).order_by('-time')
        snum = Notification.objects.filter(Q(classification="All") | Q(classification="All_HomeOwner") | Q(classification="HomeOwner", homeowner_id=homeowner_id) & Q(view=False)).order_by('-time')

        num = snum.count()
        
        
        return render(request, "homeowners/notification.html", {'msg':msg, 'num':num})
    else:
        return redirect('404')

@login_required(login_url="hsignin")
def profile(request):
    if request.user.is_homeowner is True:
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
            messages.success(request, 'Profile updated successfully', extra_tags='loginsucess')
            return redirect('viewprofile')
    
        
        return render(request, "homeowners/profile.html",{'hprofile':hprofile})
    else:
        return redirect('404')

@login_required(login_url="hsignin")
def changepassword(request):
    if request.user.is_homeowner is True:
        username = request.user.username
        hprofile = Account_HomeOwner.objects.get(username=username)
        mainhprofile = User.objects.get(username=username)
        if request.method == 'POST':
            password = request.POST.get('password')
            conformpassword = request.POST.get('conformpassword')
            
            if password==conformpassword:
                # Retrieve the user's Account_HomeOwner object and update its fields
                mainhprofile.password = make_password(password)
                mainhprofile.save()
                hprofile.password = make_password(password)
                hprofile.save() 
                messages.success(request, "Password updated successfully")
                return redirect('hsignin')
            else :
                messages.error(request, "Conform Password not match")
        return render(request, "homeowners/changepassword.html",{'hprofile':hprofile})
    else:
        return redirect('404')

@login_required(login_url="hsignin")
def viewprofile(request):
    if request.user.is_homeowner is True:
        username = request.user.username
        hprofile = Account_HomeOwner.objects.get(username=username)
        return render(request, "homeowners/viewprofile.html",{'hprofile':hprofile})
    else:
        return redirect('404')


@login_required(login_url="hsignin")
def bookings(request):
    if request.user.is_homeowner is True:
        username = request.user.username
        alldata = Account_HomeOwner.objects.get(username=username)
        ord = Order.objects.filter(homeowner_id=alldata.homeowner_id).order_by('-date', '-time')
        
        #total amount
        amount = 0
        for order in ord:
            if order.payment_amount:
                amounts = float(order.payment_amount)
                amount = amount + amounts
        amount = amount
        return render(request, "homeowners/bookings.html",{'ord':ord,'amount':amount})
    else:
        return redirect('404')
    
@login_required(login_url="hsignin")
def paymentpage(request):
    if request.user.is_homeowner is True:
        return render(request, "homeowners/paymentpage.html")
    else:
        return redirect('404')

@login_required(login_url="hsignin")
def bookingdetails(request,od):
    if request.user.is_homeowner is True:
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
            amount = request.POST['amount']
            print(amount)
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
        return render(request, "homeowners/bookingdetails.html",{'ord':ord, 'status':status, 'servicedata': servicedata, 'payable': order_payable(ord)})
    else:
        return redirect('404')

@login_required(login_url="psignin")
def requestdetails(request,rd):
    if request.user.is_professional is True:
        ord = Order.objects.get(order_id=rd)
        if ord.status == 'cancel':
            status = 'Cancel'
        elif ord.status == 'solve':
            status = 'Solve'
        else:
            status = 'Book'
        return render(request, "professionals/requestdetails.html",{'ord':ord, 'status':status, 'payable': order_payable(ord)})
    else:
        return redirect('404')

@login_required(login_url="psignin")
def request(request):
    if request.user.is_professional is True:
        username = request.user.username
        ord = Order.objects.all()
        po = Account_Professional.objects.get(username=username)
        ord = Order.objects.filter(professional_id=po.professional_id).order_by('-date', '-time')       
        amount = 0
        for order in ord:
            if order.payment_amount:
                amounts = float(order.payment_amount)
                amount = amount + amounts
        amount = amount

        return render(request, "professionals/request.html",{'ord':ord, 'po':po, 'amount':amount})
    else:
        return redirect('404')

@login_required(login_url="psignin")
def professionalprofile(request):
    if request.user.is_professional is True:
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
            return redirect('professionalviewprofile')
        return render(request, "professionals/professionalprofile.html",{'po':po})
    else:
        return redirect('404')

@login_required(login_url="psignin")
def professionalchangepassword(request):
    if request.user.is_professional is True:
        username = request.user.username
        po = Account_Professional.objects.get(username=username)
        mainpprofile = User.objects.get(username=username)
        if request.method == 'POST':
            password = request.POST.get('password')
            conformpassword = request.POST.get('conformpassword')
            if password == conformpassword:
            # Retrieve the user's Account_HomeOwner object and update its fields
                mainpprofile.password = make_password(password)
                mainpprofile.save()
                po.password = make_password(password)
                po.save() 
                messages.success(request, "Password updated successfully")
                return redirect('psignin')
            else:
                messages.error(request, "Conform Password not match")
                
        return render(request, "professionals/professionalchangepassword.html",{'po':po})
    else:
        return redirect('404')

@login_required(login_url="psignin")
def professionalviewprofile(request):
    if request.user.is_professional is True:
        username = request.user.username
        po = Account_Professional.objects.get(username=username)
        return render(request, "professionals/professionalviewprofile.html",{'po':po})
    else:
        return redirect('404')
  

@login_required(login_url="psignin")
def professionalnotification(request):
    if request.user.is_professional is True:
        username = request.user.username
        print(username)
        if username:
                professional_id = Account_Professional.objects.get(username=username)        
        msg = Notification.objects.filter(Q(classification="All") | Q(classification="All_Professional") | Q(classification="Professional", professional_id=professional_id)).order_by('-time')
        snum = Notification.objects.filter(Q(classification="All") | Q(classification="All_Professional") | Q(classification="Professional", professional_id=professional_id) & Q(view=False)).order_by('-time')
        num= snum.count()
        po = Account_Professional.objects.get(username=username)
        return render(request, "professionals/professionalnotification.html",{'msg':msg, 'num':num,'po':po})
    else:
        return redirect('404')


@login_required(login_url="adminsignin")
def adminhomepage(request):
    if request.user.is_admin is True:
        orders = list(Order.objects.select_related('professional_id').all())

        def amt(o):
            try:
                return float(o.payment_amount) if o.payment_amount else 0.0
            except (TypeError, ValueError):
                return 0.0

        today = datetime.now().date()
        month_start = today.replace(day=1)
        revenue_total = round(sum(amt(o) for o in orders), 2)
        revenue_month = round(sum(amt(o) for o in orders
                                  if o.payment_date and o.payment_date.year == today.year
                                  and o.payment_date.month == today.month), 2)
        waiting_payment = sum(1 for o in orders if o.status == 'solve' and not o.payment_amount)

        # last 6 months: bookings made + revenue collected
        months = []
        yy, mm = today.year, today.month
        for i in range(5, -1, -1):
            m2 = mm - i
            y2 = yy
            while m2 <= 0:
                m2 += 12
                y2 -= 1
            months.append((y2, m2))
        labels = [calendar.month_abbr[m2] + " " + str(y2) for (y2, m2) in months]
        bookings_series = [sum(1 for o in orders if o.date and o.date.year == y2 and o.date.month == m2)
                           for (y2, m2) in months]
        revenue_series = [round(sum(amt(o) for o in orders
                                    if o.payment_date and o.payment_date.year == y2 and o.payment_date.month == m2), 2)
                          for (y2, m2) in months]

        status_labels = ['Booked', 'Accepted', 'Solved', 'Cancelled by owner', 'Cancelled by pro']
        status_series = [sum(1 for o in orders if o.status == st)
                         for st in ['book', 'accept', 'solve', 'cancel', 'cancelbyprofessional']]

        # top earning professionals this month
        earn = {}
        for o in orders:
            if o.payment_amount and o.payment_date and o.payment_date.year == today.year and o.payment_date.month == today.month:
                earn[o.professional_id.full_name] = earn.get(o.professional_id.full_name, 0) + amt(o)
        top = sorted(earn.items(), key=lambda kv: kv[1], reverse=True)[:5]

        context = {
            'h': Account_HomeOwner.objects.count(),
            'p': Account_Professional.objects.count(),
            's': Service_List.objects.count(),
            'total_orders': len(orders),
            'revenue_total': revenue_total,
            'revenue_month': revenue_month,
            'waiting_payment': waiting_payment,
            'month_name': calendar.month_name[today.month],
            'chart_data': json.dumps({
                'labels': labels,
                'bookings': bookings_series,
                'revenue': revenue_series,
                'statusLabels': status_labels,
                'status': status_series,
                'topNames': [t[0] for t in top],
                'topEarnings': [round(t[1], 2) for t in top],
            }),
        }
        return render(request, "admin/adminhomepage.html", context)
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def admincreateservice(request):
    if request.user.is_admin is True:
        servs = Service_List.objects.all().order_by('service_list')
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
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def admincreatesubservice(request):
    if request.user.is_admin is True:
        servs = Service_List.objects.all().order_by('service_list')
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
    else:
        return redirect('404')
    
@login_required(login_url="adminsignin")
def admincreateblog(request):
    if request.user.is_admin is True:
        if request.method =="POST":
            title = request.POST.get('title')
            photo = request.FILES.get('photo')
            desc = request.POST.get('desc')
            if Blog.objects.filter(title=title).exists():
                    messages.info(request,'Sorry! Title Already Exist')
                    return redirect('admincreateblog')
            else:    
                blog = Blog(
                    title = title,
                    photo = photo,
                    desc = desc   
                )
                blog.save()
                messages.info(request,'New Blog Created')
        return render(request, "admin/admincreateblog.html")
    else:
        return redirect('404')
    
    
@login_required(login_url="adminsignin")
def adminblogdetail(request, pk):
    if request.user.is_admin is True:
        blog = Blog.objects.get(blog_id=pk)
        if request.method == "POST":
            title = request.POST.get('title')
            photo = request.FILES.get('photo')
            desc = request.POST.get('desc')
            
            # Update the existing instance with the new values
            blog.title = title
            if photo:
                blog.photo = photo
            blog.desc = desc
            blog.save()
            messages.info(request,'Sucessfull Update!!!')
            
        return render(request, "admin/adminblogdetail.html", {'blog': blog})
    else:
        return redirect('404')
    
@login_required(login_url="adminsignin")
def adminblog(request):
    if request.user.is_admin is True:
        query = request.GET.get('q')
        if query:
            blog = Blog.objects.filter(
            Q(blog_id__icontains=query) | Q(title__icontains=query) 
            )
        else:
            blog = Blog.objects.all()
        return render(request, "admin/adminblog.html",{'blog':blog})
    else:
        return redirect('404')


@login_required(login_url="adminsignin")
def adminmessage(request):
    if request.user.is_admin is True:
        msg = Message.objects.all().order_by('-msg_id')
        return render(request, "admin/adminmessage.html",{'msg':msg})
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def adminorderdetail(request,ok):
    if request.user.is_admin is True:
        ord = Order.objects.get(order_id=ok) 
        return render(request, "admin/adminorderdetail.html",{'ord':ord})
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def adminprofile(request):
    if request.user.is_admin is True:
        return render(request, "admin/adminprofile.html")
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def adminservicedetail(request, pk):
    if request.user.is_admin is True:
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
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def adminservicelist(request):
    if request.user.is_admin is True:
        query = request.GET.get('q')
        if query:
            # search for users that match the query string in any of the specified fields
            serv = All_Service.objects.filter(
            Q(service_id__icontains=query) | Q(service__icontains=query) | Q(subservice__icontains=query)
            )
        else:
        # serv = All_Service.objects.exclude(service=True)
            serv = All_Service.objects.all()
        return render(request, "admin/adminservicelist.html",{'serv':serv})
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def adminservicemandetail(request,pok):
    if request.user.is_admin is True:
        po = Account_Professional.objects.get(professional_id=pok)
        return render(request, "admin/adminservicemandetail.html",{'po':po})
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def adminservicemanlist(request):
    if request.user.is_admin is True:
        qs = Account_Professional.objects.all()
        query = request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(username__icontains=query) | Q(email__icontains=query) |
                Q(full_name__icontains=query) | Q(service__icontains=query) |
                Q(subservice__icontains=query) | Q(address__icontains=query)
            )
        service_f = request.GET.get('service') or ''
        if service_f:
            qs = qs.filter(service=service_f)
        status_f = request.GET.get('status') or ''
        if status_f == 'approved':
            qs = qs.filter(status=True)
        elif status_f == 'pending':
            qs = qs.filter(status=False)

        # earned this month, per professional
        today = datetime.now().date()
        earnings = {}
        for o in Order.objects.filter(payment_date__year=today.year, payment_date__month=today.month).exclude(payment_amount__isnull=True):
            try:
                earnings[o.professional_id_id] = earnings.get(o.professional_id_id, 0) + float(o.payment_amount)
            except (TypeError, ValueError):
                pass
        po = list(qs)
        for prof in po:
            prof.earned_month = round(earnings.get(prof.professional_id, 0), 2)

        sort = request.GET.get('sort') or 'newest'
        if sort == 'earnings':
            po.sort(key=lambda x: x.earned_month, reverse=True)
        elif sort == 'rating':
            po.sort(key=lambda x: (x.ratings or 0, x.num_ratings or 0), reverse=True)

        services = Service_List.objects.all().order_by('service_list')
        return render(request, "admin/adminservicemanlist.html", {
            'po': po, 'services': services,
            'f': {'q': query or '', 'service': service_f, 'status': status_f, 'sort': sort},
        })
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def adminuserdetail(request,hk):
    if request.user.is_admin is True:
        ho = Account_HomeOwner.objects.get(homeowner_id=hk)
        return render(request, "admin/adminuserdetail.html",{'ho':ho})
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def adminusermanlist(request):
    if request.user.is_admin is True:
        query = request.GET.get('q')
        if query:
            # search for users that match the query string in any of the specified fields
            ho = Account_HomeOwner.objects.filter(
            Q(homeowner_id__icontains=query) | Q(username__icontains=query) | Q(email__icontains=query) | Q(full_name__icontains=query) 
            )
        else:
            ho =Account_HomeOwner.objects.all()
        return render(request, 'admin/adminusermanlist.html',{'ho':ho})
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def adminvieworder(request):
    if request.user.is_admin is True:
        qs = Order.objects.select_related('professional_id', 'homeowner_id').all()
        query = request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(status__icontains=query) |
                Q(professional_id__full_name__icontains=query) |
                Q(homeowner_id__full_name__icontains=query) |
                Q(address__icontains=query)
            )
        status_f = request.GET.get('status') or ''
        if status_f:
            qs = qs.filter(status=status_f)
        payment_f = request.GET.get('payment') or ''
        if payment_f == 'paid':
            qs = qs.exclude(payment_amount__isnull=True)
        elif payment_f == 'waiting':
            qs = qs.filter(payment_amount__isnull=True, status='solve')
        elif payment_f in ('Cash', 'Khalti'):
            qs = qs.filter(payment_method=payment_f)
        date_from = request.GET.get('from') or ''
        date_to = request.GET.get('to') or ''
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        sort = request.GET.get('sort') or 'newest'
        if sort == 'oldest':
            ord_list = list(qs.order_by('date', 'time'))
        elif sort == 'amount':
            def amt(o):
                try:
                    return float(o.payment_amount) if o.payment_amount else 0.0
                except (TypeError, ValueError):
                    return 0.0
            ord_list = sorted(qs, key=amt, reverse=True)
        else:
            ord_list = list(qs.order_by('-date', '-time'))
        return render(request, "admin/adminvieworder.html", {
            'ord': ord_list,
            'f': {'q': query or '', 'status': status_f, 'payment': payment_f,
                  'from': date_from, 'to': date_to, 'sort': sort},
        })
    else:
        return redirect('404')


@login_required(login_url="adminsignin")
def adminnotification(request):
    if request.user.is_admin is True:
        msg = Notification.objects.filter(Q(classification="All") | Q(classification="Admin")).order_by('-time')
        snum = Notification.objects.filter(Q(classification="All") | Q(classification="Admin") & Q(view=False)).order_by('-time')
        num= snum.count() 
        return render(request, "admin/adminnotification.html",{'msg':msg, 'num':num})
    else:
        return redirect('404')


@login_required(login_url="adminsignin")  
def ordertable(request,professional_id):
    orders = Order.objects.filter(professional_id=professional_id).order_by('-date')
    korders = Order.objects.filter(professional_id=professional_id, payment_method='Khalti').order_by('-date')
    #total amount
    amount = 0
    for order in orders:
        if order.payment_amount:
            amounts = float(order.payment_amount)
            amount = amount + amounts
    amount = amount    
    
    #total maount via khalti
    kamount = 0
    for korder in korders:
        if korder.payment_amount:
            kamounts = float(korder.payment_amount)
            kamount = kamount + kamounts
    kamount = kamount    
    return render(request, 'admin/ordertable.html', {'orders':orders,'amount':amount,'kamount':kamount,'korders':korders})

@login_required(login_url="adminsignin")
def notify(request):
    if request.user.is_admin is True:
        classificationss = [choice[1] for choice in Notification.CLASSIFICATION_CHOICES]
        homeownerss = Account_HomeOwner.objects.all().order_by('username')
        professionalss = Account_Professional.objects.all().order_by('username')

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
    else:
        return redirect('404')





@login_required(login_url="adminsignin")
def deleteservice(request, service_id):
    if request.user.is_admin is True:
        serv = All_Service.objects.filter(service_id = service_id).delete() 
        return redirect("adminservicelist")
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def deleteservicelist(request, servicelist_id):
    if request.user.is_admin is True:
        serv = Service_List.objects.filter(servicelist_id = servicelist_id).delete() 
        return redirect("admincreateservice")
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def deleteuser(request, homeowner_id):
    if request.user.is_admin is True:
        ho = Account_HomeOwner.objects.filter(homeowner_id = homeowner_id).delete() 
        return redirect("adminusermanlist")
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def deleteserviceman(request, professional_id):
    if request.user.is_admin is True:
        po = Account_Professional.objects.filter(professional_id = professional_id).delete() 
        return redirect("adminservicemanlist")
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def deleteorder(request, order_id):
    if request.user.is_admin is True:
        ord = Order.objects.filter(order_id = order_id).delete() 
        return redirect("adminvieworder")
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def deletemsg(request, msg_id):
    if request.user.is_admin is True:
        msg = Message.objects.filter(msg_id = msg_id).delete() 
        return redirect("adminmessage")
    else:
        return redirect('404')
    
@login_required(login_url="adminsignin")
def deleteblog(request, blog_id):
    if request.user.is_admin is True:
        blog = Blog.objects.filter(blog_id = blog_id).delete() 
        return redirect("adminblog")
    else:
        return redirect('404')




@login_required(login_url="adminsignin")
def activate(request, professional_id):
    if request.user.is_admin is True:
        instance = get_object_or_404(Account_Professional, pk=professional_id)
        ins = get_object_or_404(User, pk=instance.user.pk)
        instance.status = not instance.status
        ins.is_active = not ins.is_active
        instance.save()
        ins.save()
        previous_url = request.META.get('HTTP_REFERER')
        return redirect(previous_url)
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def update_my_model(request, service_id):
    if request.user.is_admin is True:
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
    else:
        return redirect('404')


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
                        notification= f"You received a {rating}-star rating from {homeowner.full_name}.",
                        classification="Professional",
                        professional_id = prof
                        )
                    notification.save()
                    notifications = Notification.objects.create(
                        notification= f"Thank you for rating {prof.full_name} ({rating} stars).",
                        classification="HomeOwner",
                        homeowner_id = homeowner
                        )
                    notifications.save()
                    notificationss = Notification.objects.create(
                        notification= f"{homeowner.full_name} rated {prof.full_name} {rating} stars.",
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

# def notificationnumber(request):
#     print("notificationnumber view called")
#     username = request.user.username
#     if username:
#         homeowner_id = Account_HomeOwner.objects.get(username=username)
#     msg = Notification.objects.filter(Q(classification="All") | Q(classification="All_HomeOwner") | Q(classification="HomeOwner", homeowner_id=homeowner_id)).order_by('-time')
#     num = msg.count()
#     print(num)
#     return render(request, "homeowners/hbases.html", {'num': num})

@login_required(login_url="hsignin")
def update_notification_view(request):
    if request.user.is_homeowner is True:
        if request.method == 'POST':
            not_id = request.POST.get('not_id')
            notification = Notification.objects.get(not_id=not_id)
            notification.view = True
            notification.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect('404')

@login_required(login_url="psignin")
def pupdate_notification_view(request):
    if request.user.is_professional is True:
        if request.method == 'POST':
            not_id = request.POST.get('not_id')
            notification = Notification.objects.get(not_id=not_id)
            notification.view = True
            notification.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect('404')

@login_required(login_url="adminsignin")
def aupdate_notification_view(request):
    if request.user.is_admin is True:
        if request.method == 'POST':
            not_id = request.POST.get('not_id')
            notification = Notification.objects.get(not_id=not_id)
            notification.view = True
            notification.save()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return redirect('404')

@login_required(login_url="hsignin")
def notification_status(request):
    """JSON feed polled by the navbar bell: unread count + newest notification.

    Serves whichever role the logged-in user has, reusing the same
    classification filters as the three notification pages.
    """
    user = request.user
    qs = None
    if user.is_homeowner:
        owner = Account_HomeOwner.objects.filter(username=user.username).first()
        if owner:
            qs = Notification.objects.filter(
                Q(classification="All") | Q(classification="All_HomeOwner") |
                Q(classification="HomeOwner", homeowner_id=owner)
            )
    elif user.is_professional:
        prof = Account_Professional.objects.filter(username=user.username).first()
        if prof:
            qs = Notification.objects.filter(
                Q(classification="All") | Q(classification="All_Professional") |
                Q(classification="Professional", professional_id=prof)
            )
    elif user.is_admin:
        qs = Notification.objects.filter(Q(classification="All") | Q(classification="Admin"))

    if qs is None:
        return JsonResponse({'count': 0, 'latest_id': 0, 'latest_text': ''})

    newest = qs.order_by('-not_id').values_list('not_id', 'notification').first()
    return JsonResponse({
        'count': qs.filter(view=False).count(),
        'latest_id': newest[0] if newest else 0,
        'latest_text': newest[1] if newest else '',
    })


@login_required(login_url="psignin")
def online(request, usernames):
    if request.user.is_professional is True:
        professional = Account_Professional.objects.filter(username=usernames).first()
        professional_id = professional.professional_id
        obj = get_object_or_404(Account_Professional, pk=professional_id)
        obj.online = not obj.online
        obj.save()
        previous_url = request.META.get('HTTP_REFERER')
        return redirect(previous_url)
    else:
        return redirect('404')






                
                
                
    













@login_required(login_url="hsignin")
def mark_all_read(request):
    """POST: mark every unread notification for the logged-in role as read."""
    if request.method == 'POST':
        user = request.user
        qs = None
        if user.is_homeowner:
            owner = Account_HomeOwner.objects.filter(username=user.username).first()
            if owner:
                qs = Notification.objects.filter(
                    Q(classification="All") | Q(classification="All_HomeOwner") |
                    Q(classification="HomeOwner", homeowner_id=owner))
        elif user.is_professional:
            prof = Account_Professional.objects.filter(username=user.username).first()
            if prof:
                qs = Notification.objects.filter(
                    Q(classification="All") | Q(classification="All_Professional") |
                    Q(classification="Professional", professional_id=prof))
        elif user.is_admin:
            qs = Notification.objects.filter(Q(classification="All") | Q(classification="Admin"))
        updated = qs.filter(view=False).update(view=True) if qs is not None else 0
        return JsonResponse({'ok': True, 'updated': updated})
    return JsonResponse({'ok': False}, status=400)


@login_required(login_url="hsignin")
def check_availability(request, prof_id):
    """Live slot check while the homeowner picks a date and time."""
    prof = Account_Professional.objects.filter(professional_id=prof_id).first()
    date_str = request.GET.get('date', '')
    time_str = request.GET.get('time', '')
    if not (prof and date_str and time_str):
        return JsonResponse({'available': True, 'message': ''})
    try:
        selected = datetime.combine(
            datetime.strptime(date_str, '%Y-%m-%d').date(),
            datetime.strptime(time_str, '%H:%M').time())
    except ValueError:
        return JsonResponse({'available': True, 'message': ''})
    now = datetime.now()
    if selected < now:
        return JsonResponse({'available': False, 'message': 'That time has already passed. Please pick a future time.'})
    if (selected.date() - now.date()).days > 30:
        return JsonResponse({'available': False, 'message': 'Bookings can be made at most 30 days in advance.'})
    if slot_conflict(prof, selected):
        return JsonResponse({'available': False, 'message': prof.full_name + ' is not available at that time - another booking is within 1 hour. Please take another slot.'})
    return JsonResponse({'available': True, 'message': 'Slot available.'})


@login_required(login_url="psignin")
def update_work_amount(request, order_id):
    """Professional corrects the hours or amount they entered, while unpaid."""
    if request.user.is_professional is True and request.method == 'POST':
        prof = Account_Professional.objects.filter(username=request.user.username).first()
        instance = get_object_or_404(Order, order_id=order_id, professional_id=prof)
        if instance.status == 'solve' and instance.payment_amount is None:
            if request.POST.get('chargemode') == 'fixed':
                try:
                    instance.quoted_amount = float(request.POST.get('fixedamount'))
                    instance.save()
                    messages.success(request, 'Billing updated.', extra_tags='loginsucess')
                except (TypeError, ValueError):
                    messages.error(request, 'Please enter a valid amount.')
            else:
                try:
                    instance.totaltimehour = float(request.POST.get('totalhour'))
                    instance.quoted_amount = None
                    instance.save()
                    messages.success(request, 'Billing updated.', extra_tags='loginsucess')
                except (TypeError, ValueError):
                    messages.error(request, 'Please enter valid hours.')
        return redirect('requestdetails', rd=order_id)
    return redirect('404')


@login_required(login_url="psignin")
def confirm_cash_payment(request, order_id):
    """Professional confirms the cash was received - closes the job for both sides."""
    if request.user.is_professional is True and request.method == 'POST':
        prof = Account_Professional.objects.filter(username=request.user.username).first()
        instance = get_object_or_404(Order, order_id=order_id, professional_id=prof)
        if instance.status == 'solve' and instance.payment_amount is None:
            instance.payment_amount = str(order_payable(instance))
            instance.payment_method = 'Cash'
            instance.payment_date = datetime.now()
            instance.save()
            Notification.objects.create(
                notification=f"Payment of Rs. {instance.payment_amount} received in cash for booking #{instance.order_id}. Service completed.",
                classification="HomeOwner", homeowner_id=instance.homeowner_id)
            Notification.objects.create(
                notification=f"You confirmed the cash payment of Rs. {instance.payment_amount} for request #{instance.order_id}.",
                classification="Professional", professional_id=prof)
            messages.success(request, 'Cash payment recorded. Service completed!', extra_tags='loginsucess')
        return redirect('requestdetails', rd=order_id)
    return redirect('404')


@login_required(login_url="adminsignin")
def adminaisettings(request):
    if request.user.is_admin is True:
        config = SiteConfig.get()
        if request.method == 'POST':
            config.gemini_api_key = request.POST.get('gemini_api_key', '').strip()
            config.gemini_model = request.POST.get('gemini_model', '').strip() or 'gemini-2.0-flash'
            config.assistant_enabled = request.POST.get('assistant_enabled') == 'on'
            config.save()
            messages.success(request, 'AI assistant settings saved.', extra_tags='loginsucess')
            return redirect('adminaisettings')
        return render(request, "admin/adminaisettings.html", {'config': config})
    else:
        return redirect('404')


ASSISTANT_INSTRUCTIONS = (
    "You are SewaGhar Sahayogi, the help assistant for SewaGhar (sewaghar.regmicode.com), "
    "a Nepali home-services marketplace connecting home owners in Kathmandu valley with verified "
    "professionals (electricians, plumbers, carpenters, painters, cleaners and more). "
    "Only answer questions about using SewaGhar. Key facts: "
    "Home owners sign up at /hsignup and log in at /hsignin. Professionals sign up at /psignup "
    "(photo and citizenship card needed; the admin approves the account) and log in at /psignin. "
    "Booking: Services page, choose a service, choose a sub-service, pick a professional "
    "(see ratings, rate per hour, location), choose date and time (today up to 30 days ahead; slots "
    "within 1 hour of an existing booking are unavailable), pin the home location on the map, "
    "optionally offer your own price (between 80 and 150 percent of the listed rate) and describe the work, then book. "
    "The professional accepts or cancels. After finishing, the professional enters hours worked or a "
    "fixed amount; the home owner pays via Khalti or cash (the professional can confirm cash received, "
    "which completes the service). After completion the home owner can rate the professional 1-5 stars. "
    "Password reset works via OTP sent to the registered email. Notifications are under the bell icon. "
    "Contact details you may share: email sewagharservice@gmail.com, phone +977 9863144095, "
    "office Balaju-8, Kathmandu, Nepal. There is also a Contact Us form at the bottom of the home page. "
    "Answer in the user's language - English or Nepali. Keep answers short and friendly. "
    "If asked anything unrelated to SewaGhar, politely say you can only help with SewaGhar."
)


@csrf_exempt
def assistant_chat(request):
    """Proxy one chat turn to Google Gemini using the admin-configured key and model."""
    if request.method != 'POST':
        return JsonResponse({'reply': ''}, status=405)
    config = SiteConfig.get()
    if not config.assistant_enabled or not config.gemini_api_key:
        return JsonResponse({'reply': 'The assistant is not available right now. Please email sewagharservice@gmail.com for help.'})
    try:
        payload = json.loads(request.body or '{}')
    except ValueError:
        return JsonResponse({'reply': 'Sorry, I could not read that message.'})
    contents = []
    for turn in (payload.get('history') or [])[-10:]:
        role = 'model' if turn.get('role') == 'assistant' else 'user'
        text = str(turn.get('text') or '')[:2000]
        if text:
            contents.append({'role': role, 'parts': [{'text': text}]})
    message = str(payload.get('message') or '').strip()[:2000]
    if not message:
        return JsonResponse({'reply': 'Please type a question about SewaGhar.'})
    contents.append({'role': 'user', 'parts': [{'text': message}]})
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + config.gemini_model + ":generateContent?key=" + config.gemini_api_key
    body = {
        'system_instruction': {'parts': [{'text': ASSISTANT_INSTRUCTIONS}]},
        'contents': contents,
        'generationConfig': {'maxOutputTokens': 512, 'temperature': 0.4},
    }
    try:
        resp = requests.post(url, json=body, timeout=25)
        data = resp.json()
        reply = data['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return JsonResponse({'reply': 'Sorry, I could not answer right now. Please try again in a moment.'})
    return JsonResponse({'reply': reply})


def robots_txt(request):
    content = "User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: https://sewaghar.regmicode.com/sitemap.xml\n"
    return HttpResponse(content, content_type="text/plain")


def sitemap_xml(request):
    base = "https://sewaghar.regmicode.com"
    pages = ["/aboutus", "/blog", "/hsignup", "/psignup/", "/hsignin", "/psignin",
             "/privacypolicy", "/termsandcondition"]
    items = "".join('<url><loc>' + base + p + '</loc><changefreq>weekly</changefreq></url>' for p in pages)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           '<url><loc>' + base + '/home</loc><changefreq>daily</changefreq><priority>1.0</priority></url>'
           + items + '</urlset>')
    return HttpResponse(xml, content_type="application/xml")


def contact_us(request):
    """Public Contact Us form on the home page."""
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        phone = (request.POST.get('phone') or '').strip()
        message_text = (request.POST.get('message') or '').strip()
        if name and message_text and (email or phone):
            ContactMessage.objects.create(name=name, email=email, phone=phone, message=message_text)
            Notification.objects.create(
                notification=f"New contact message from {name} ({email or phone}).",
                classification="Admin")
            messages.success(request, 'Thank you! We received your message and will get back to you soon.', extra_tags='loginsucess')
        else:
            messages.error(request, 'Please fill your name, a message, and an email or phone number.')
    return redirect('home')


@login_required(login_url="adminsignin")
def admincontacts(request):
    if request.user.is_admin is True:
        query = request.GET.get('q')
        if query:
            msgs = ContactMessage.objects.filter(
                Q(name__icontains=query) | Q(email__icontains=query) |
                Q(phone__icontains=query) | Q(message__icontains=query))
        else:
            msgs = ContactMessage.objects.all()
        return render(request, "admin/admincontacts.html", {'msgs': msgs})
    else:
        return redirect('404')


@login_required(login_url="adminsignin")
def deletecontact(request, contact_id):
    if request.user.is_admin is True:
        ContactMessage.objects.filter(contact_id=contact_id).delete()
        return redirect("admincontacts")
    else:
        return redirect('404')


@login_required(login_url="hsignin")
def order_state(request, order_id):
    """Tiny JSON fingerprint of an order; detail pages poll it to live-refresh."""
    o = Order.objects.filter(order_id=order_id).select_related('homeowner_id', 'professional_id').first()
    if not o:
        return JsonResponse({}, status=404)
    u = request.user
    allowed = (u.is_admin
               or (u.is_homeowner and o.homeowner_id.username == u.username)
               or (u.is_professional and o.professional_id.username == u.username))
    if not allowed:
        return JsonResponse({}, status=403)
    return JsonResponse({
        'status': o.status,
        'paid': bool(o.payment_amount),
        'amount': o.payment_amount,
        'hours': o.totaltimehour,
        'quoted': o.quoted_amount,
        'rated': o.ratingcheck,
    })


def google_verify(request):
    return HttpResponse("google-site-verification: google5d2ebb19aca3f044.html", content_type="text/html")
