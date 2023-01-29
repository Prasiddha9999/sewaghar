from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your CustomUsermanager models here.
# class CustomUserManger(BaseUserManager):
#     def _create_user(self, email, password, full_name, number **extra_fields):
#         if not email:
#             raise ValueError("Email must be Provided")
#         if not password:
#             raise ValueError('Password is not provided')
        
#         user = self.model(
#             email = self.normalize_email(email),
#             full_name = full_name,
#             number = number,
#             **extra_fields
#         )
        
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
#     def create_user(self, email, password, full_name, number, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_active', True)
#         extra_fields.setdefault('is_superuser', False)
#         return self._create_user(email, password, full_name, number, password, **extra_fields)
         
#     def create_superuser(self, email, password, full_name, number, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_active', True)
#         extra_fields.setdefault('is_superuser', True)
#         return self._create_user(email, password, full_name, number, password, **extra_fields)        
# Create your models here.

class Account_HomeOwner(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True, unique=True, max_length=100)
    number = models.CharField(max_length=15)
    address = models.TextField()
    password = models.CharField(max_length=100)
    photo = models.ImageField()
    
    def __str__(self):
            return self.full_name
         
class All_Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service = models.CharField(max_length=255)
    subservice = models.CharField(max_length=255)
    photo = models.ImageField()
    desc = models.CharField(max_length=255)
        
  

    
    
    # is_staff = models.BooleanField(default=True)
    # is_active = models.BooleanField(default=True)
    # is_superuser = models.BooleanField(default=False)
    
    # objects = CustomUserManger()
    
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['full_name','number']
    
    # class Meta:
    #     verbose_name = 'User'
    #     verbose_name_plural = 'Users'

   