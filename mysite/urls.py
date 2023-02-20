from django.urls import path
from .views import activate
from .views import update_my_model

from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path("blog",views.blog, name="blog"),
    path("aboutus",views.aboutus, name="aboutus"),
    path("privacypolicy",views.privacypolicy, name="privacypolicy"),
    path("termsandcondition",views.termsandcondition, name="termsandcondition"),
    path("service",views.service, name="service"),
    path("subservice/<str:sk>",views.subservice, name="subservice"),
    path("servicetime/<str:bk>",views.servicetime, name="servicetime"),
    path("servicemanlist/<str:slk>",views.servicemanlist, name="servicemanlist"),
    path("book/<int:sml>",views.book, name="book"),
    path("unbook",views.unbook, name="unbook"),
    path("notification",views.notification, name="notification"),
    path("profile",views.profile, name="profile"),
    path("bookings",views.bookings, name="bookings"),
    path("bookingdetails",views.bookingdetails, name="bookingdetails"),
    path("requestdetails",views.requestdetails, name="requestdetails"),
    path("request",views.request, name="request"),
    path("professionalprofile",views.professionalprofile, name="professionalprofile"),
    path("professionalnotification",views.professionalnotification, name="professionalnotification"),
    path("adminhomepage",views.adminhomepage, name="adminhomepage"),
    path("admincreateservice",views.admincreateservice, name="admincreateservice"),
    
    path("admincreatesubservice",views.admincreatesubservice, name="admincreatesubservice"),
    
    path("adminmessage",views.adminmessage, name="adminmessage"),

    path("adminprofile",views.adminprofile, name="adminprofile"),
    
    path("adminservicedetail/<int:pk>",views.adminservicedetail, name="adminservicedetail"),
    
    path("adminservicelist",views.adminservicelist, name="adminservicelist"),
    
    path("adminservicemandetail/<int:pok>",views.adminservicemandetail, name="adminservicemandetail"),
    
    path("adminservicemanlist",views.adminservicemanlist, name="adminservicemanlist"),
    
    path("adminuserdetail/<int:hk>",views.adminuserdetail, name="adminuserdetail"),
    
    path("adminusermanlist",views.adminusermanlist, name="adminusermanlist"),
    
    path("adminvieworder",views.adminvieworder, name="adminvieworder"),
    
    path("adminorderdetail/<int:ok>",views.adminorderdetail, name="adminorderdetail"),
    
    path("adminnotification",views.adminnotification, name="adminnotification"),
    
    
    
    
    path("deleteservice/<str:service_id>",views.deleteservice, name="deleteservice"),
    path("deleteservicelist/<str:servicelist_id>",views.deleteservicelist, name="deleteservicelist"),
    path("deleteuser/<str:homeowner_id>",views.deleteuser, name="deleteuser"),
    path("deleteserviceman/<str:professional_id>",views.deleteserviceman, name="deleteserviceman"),
    path("deleteorder/<str:order_id>",views.deleteorder, name="deleteorder"),
    path("deletemsg/<str:msg_id>",views.deletemsg, name="deletemsg"),

    path('activate/<str:professional_id>/', views.activate, name='activate'),
    path('update_my_model/<str:service_id>/', views.update_my_model, name='update_my_model'),
    path('usermessage/subservice/save', views.usermessage, name='usermessage'),
]















