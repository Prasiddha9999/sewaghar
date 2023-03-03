from django.urls import path

from account import views

urlpatterns = [
    path('hsignin',views.hsignin, name="hsignin"),
    path("psignin",views.psignin, name="psignin"),
    path("hsignup",views.hsignup, name="hsignup"),
    path("psignup/",views.psignup, name="psignup"),
    path("logout",views.logout, name="logout"),
    path("adminsignin",views.adminsignin, name="adminsignin"),
]
