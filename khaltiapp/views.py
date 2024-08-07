from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required

from account.models import Order
import json
import requests
from datetime import datetime
from django.contrib import messages


# Create your views here.
@login_required(login_url="hsignin")
def config(request):
    if request.method == 'POST':
        amount = float(request.POST['amount'])
        orderid = request.POST['orderid']
    amount=amount
    return render(request,"config.html",{"amount":amount, "orderid":orderid})


@login_required(login_url="hsignin")
def verify(request):   
    if request.method == 'POST':
        payload = json.loads(request.body)
        orderid = payload['product_identity']
        # process the payload data here
        token = payload['token']
        amount = payload['amount']
        idx = payload['idx']

        url = "https://khalti.com/api/v2/payment/verify/"

        payload = {
            'token': token,
            'amount': amount
        }

        headers = {
            'Authorization': 'Key test_secret_key_736d8be761e4405e9d5a9155c7667305'
        }

        response = requests.request("POST", url, headers=headers, json=payload)
        if response.status_code != 200:
            print('Payment verification failed:', response.content)
            return JsonResponse({'status': 'error'})
        else:
            # if the request is authenticated, save the data in the Order table
            # messages.success(request, "Payment Successfully")
            orders = Order.objects.get(order_id=orderid)
            orders.payment_token = token
            orders.payment_idx = idx
            orders.payment_amount = float(amount/100)
            orders.payment_date = datetime.now()
            orders.payment_method = "Khalti"
            orders.save()
            return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

  