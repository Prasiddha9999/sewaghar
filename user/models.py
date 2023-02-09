from django.db import models
from django.utils import timezone

class Account_HomeOwner(models.Model):
    homeowner_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True, unique=True, max_length=100)
    number = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    photo = models.ImageField()
    register = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering=('-register',)
    
    def __str__(self):
            return self.full_name


GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Others'),
    )  
       
class Account_Professional(models.Model):
    professional_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True, unique=True, max_length=100)
    number = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    photo = models.ImageField()
    citizenship = models.ImageField()
    number = models.CharField(max_length=3)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    register = models.DateTimeField(default=timezone.now)
    service = models.CharField(max_length=100)
    subservice = models.CharField(max_length=100)
    exprience = models.CharField(max_length=100)
    desc = models.TextField(max_length=1000)
    status = models.CharField(max_length=1000, default='pending')
    
    class Meta:
        ordering=('-register',)   
     
    def __str__(self):
            return self.full_name
         
class All_Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service = models.CharField(max_length=255)
    subservice = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='images/', default=None)
    desc = models.TextField(max_length=255)

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    service = models.CharField(max_length=255)
    date = models.DateField((u"Appointment Date"), blank=True)
    time = models.TimeField((u"Appointment Time"), blank=True)
    subservice = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default='Not-Solved')
    rating = models.IntegerField(max_length=5)
    rateperhour = models.CharField(max_length=10)
    houseno = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    professional_id = models.CharField(max_length=50)
    homeowner_id = models.CharField(max_length=50)
    message = models.TextField(max_length=500)
    address = models.CharField(max_length=255)
    
    
class Message(models.Model):
    msg_id = models.AutoField(primary_key=True)
    message = models.TextField(max_length=500) 
    professional_id = models.CharField(max_length=50, null=True, blank=True)
    homeowner_id = models.CharField(max_length=50, null=True, blank=True)
    
class Service_List(models.Model):
    servicelist_id = models.AutoField(primary_key=True)
    service_list = models.CharField(max_length=255)
       
