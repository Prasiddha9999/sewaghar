from django.urls import path

from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path("blog",views.blog, name="blog"),
    path("aboutus",views.aboutus, name="aboutus"),
    path("privacypolicy",views.privacypolicy, name="privacypolicy"),
    path("termsandcondition",views.termsandcondition, name="termsandcondition"),
    path("service",views.service, name="service"),

]
