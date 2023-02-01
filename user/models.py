from django.db import models
from django.utils import timezone

class Account_HomeOwner(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True, unique=True, max_length=100)
    number = models.CharField(max_length=15)
    address = models.TextField()
    password = models.CharField(max_length=100)
    photo = models.ImageField()
    register = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering=('-register',)
    
    def __str__(self):
            return self.full_name
         
class All_Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service = models.CharField(max_length=255)
    subservice = models.CharField(max_length=255)
    photo = models.ImageField()
    desc = models.CharField(max_length=255)
        
