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
    path("bookingdetail",views.bookingdetail, name="bookingdetail"),
]


