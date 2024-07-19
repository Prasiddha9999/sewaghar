from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Account_HomeOwner)
admin.site.register(All_Service)
admin.site.register(Account_Professional)
admin.site.register(Order)
admin.site.register(Message)
admin.site.register(Service_List)
admin.site.register(User)
admin.site.register(Notification)
admin.site.register(Blog)