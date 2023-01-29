from django.urls import path

from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path("blog",views.blog, name="blog"),
    path("aboutus",views.aboutus, name="aboutus"),
    path("privacypolicy",views.privacypolicy, name="privacypolicy"),
    path("termsandcondition",views.termsandcondition, name="termsandcondition"),
    path("service",views.service, name="service"),
    path("subservice",views.subservice, name="subservice"),
    path("servicetime",views.servicetime, name="servicetime"),
    path("servicemanlist",views.servicemanlist, name="servicemanlist"),
    path("book",views.book, name="book"),
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
    path("adminmessage",views.adminmessage, name="adminmessage"),
    path("adminorderdetail",views.adminorderdetail, name="adminorderdetail"),
    path("adminprofile",views.adminprofile, name="adminprofile"),
    path("adminservicedetail",views.adminservicedetail, name="adminservicedetail"),
    path("adminservicelist",views.adminservicelist, name="adminservicelist"),
    path("adminservicemandetail",views.adminservicemandetail, name="adminservicemandetail"),
    path("adminservicemanlist",views.adminservicemanlist, name="adminservicemanlist"),
    path("adminuserdetail",views.adminuserdetail, name="adminuserdetail"),
    path("adminusermanlist",views.adminusermanlist, name="adminusermanlist"),
    path("adminvieworder",views.adminvieworder, name="adminvieworder"),
    path("adminnotification",views.adminnotification, name="adminnotification"),
]














