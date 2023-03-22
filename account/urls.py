from django.urls import path

from account import views

urlpatterns = [
    path('hsignin',views.hsignin, name="hsignin"),
    path("psignin",views.psignin, name="psignin"),
    path("hsignup",views.hsignup, name="hsignup"),
    path("psignup/",views.psignup, name="psignup"),
    path("user_logout",views.user_logout, name="user_logout"),
    path("adminsignin",views.adminsignin, name="adminsignin"),
    path("subservice",views.loadSubService,name="loadSubService")
]
