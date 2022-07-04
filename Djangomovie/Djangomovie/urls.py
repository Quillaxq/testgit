"""Djangomovie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path as url
from django.urls import path

from user import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('', views.pages),
    path('base/', views.base),
    path('all/', views.all),
    path('movieinformation/', views.movieinformation),
    path('index/', views.index, name='index'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'register/', views.register, name='register'),
    path('movie_show/', views.pages),
    path('analyse_data/', views.analyze),
    path('search/', views.search),
    path('classify/', views.classify),
]
