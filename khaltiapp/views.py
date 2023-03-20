from django.shortcuts import render, redirect

# Create your views here.
def config(request):
    if request.method == 'POST':
        amount = request.POST['amount']
    amount=amount
    return render(request,"config.html",{"amount":amount})
