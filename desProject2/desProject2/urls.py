"""desProject2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from chat import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('chat/', views.chat, name='chat'),
    path('test/', views.test, name='test'),
    path('key/', views.key, name='key'),
    path('logout/', views.logout, name='logout'),
    path('key/createApp/', views.create_key, name='create_key'),
    path('key/getApp/', views.get_app, name='get_app'),
    path('key/acceptApp/', views.accept_app, name='accept_app'),
    path('key/rejectApp/', views.reject_app, name='reject_app'),
    path('chat/checkKey/', views.check_key, name='check_key'),
    path('chat/loadMsg/', views.load_msg, name='load_msg'),
    path('session/id/', views.get_id, name='get_id'),
]