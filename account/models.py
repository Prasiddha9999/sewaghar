from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    password = models.CharField(max_length=100)
    is_admin  = models.BooleanField('Is admin', default=False)
    is_homeowner  = models.BooleanField('Is homeowner', default=False)
    is_professional  = models.BooleanField('Is professional', default=False)


class Account_HomeOwner(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    homeowner_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True, unique=True, max_length=100)
    number = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='images')
    otp = models.CharField(max_length=6, default="00000")
    register = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering=('-register',)
        
    # USERNAME_FIELD = 'email'
    
    def __str__(self):
            return self.username


GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    )  
       
class Account_Professional(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    professional_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField(db_index=True, unique=True, max_length=100)
    number = models.CharField(max_length=15)
    address = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    age = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='images')
    citizenship = models.ImageField(upload_to='images')
    citizenships = models.ImageField(upload_to='images')
    number = models.CharField(max_length=100)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES)
    register = models.DateTimeField(default=timezone.now)
    service = models.CharField(max_length=100)
    subservice = models.CharField(max_length=100)
    exprience = models.CharField(max_length=100)
    rateperhour = models.CharField(max_length=10, blank=True, null=True)
    desc = models.TextField(max_length=1000)
    status = models.BooleanField(default=False)
    ratings = models.IntegerField(default=0)
    num_ratings = models.IntegerField(default=0)
    otp = models.CharField(max_length=6, default="00000")
    online = models.BooleanField(default=True)
    
    class Meta:
        ordering=('-register',)   
     
    def __str__(self):
        return self.username

    def average_rating(self):
        if self.num_ratings > 0:
            return self.total_rating / self.num_ratings
        else:
            return 0
         
class All_Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service = models.CharField(max_length=255)
    subservice = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='images', default=None)
    desc = models.TextField(max_length=255)

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    date = models.DateField((u"Appointment Date"), blank=True)
    time = models.TimeField((u"Appointment Time"), blank=True)
    STATUS_CHOICES = (
        ('book', 'Book'),
        ('cancel', 'Cancel'),
        ('solve', 'Solve'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='book')
    houseno = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    professional_id = models.ForeignKey(Account_Professional, on_delete=models.CASCADE)
    homeowner_id = models.ForeignKey(Account_HomeOwner, on_delete=models.CASCADE)
    message = models.TextField( null=True, blank=True, max_length=500)
    address = models.CharField(max_length=255)
    payment_amount = models.CharField(max_length=255,  null=True, blank=True)
    payment_idx = models.CharField(max_length=255,  null=True, blank=True)
    payment_token = models.CharField(max_length=255,  null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=255, null=True, blank=True)
    totaltimehour = models.FloatField(null=True, blank=True)
    ratingcheck = models.BooleanField(default=False)
    
    
class Message(models.Model):
    msg_id = models.AutoField(primary_key=True)
    message = models.TextField(max_length=500) 
    professional_id = models.ForeignKey(Account_Professional, on_delete=models.CASCADE, null=True, blank=True)
    homeowner_id = models.ForeignKey(Account_HomeOwner, on_delete=models.CASCADE, null=True, blank=True)
    
class Service_List(models.Model):
    servicelist_id = models.AutoField(primary_key=True)
    service_list = models.CharField(max_length=255)
    
class Notification(models.Model):
    not_id = models.AutoField(primary_key=True)
    professional_id = models.ForeignKey(Account_Professional, on_delete=models.CASCADE, null=True, blank=True)
    homeowner_id = models.ForeignKey(Account_HomeOwner, on_delete=models.CASCADE, null=True, blank=True)
    notification = models.CharField(max_length=255)
    CLASSIFICATION_CHOICES = (
        ('HomeOwner', 'HomeOwner'),
        ('Professional', 'Professional'),
        ('Admin', 'Admin'),
        ('All_HomeOwner', 'All_HomeOwner'),
        ('All_Professional', 'All_Professional'),
        ('All', 'All'),
    )
    classification = models.CharField(max_length=50, choices=CLASSIFICATION_CHOICES)
    time = models.DateTimeField(auto_now_add=True)
    view = models.BooleanField(default=False)

       
