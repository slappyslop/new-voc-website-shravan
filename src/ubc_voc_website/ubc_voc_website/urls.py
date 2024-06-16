"""
URL configuration for ubc_voc_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.views.generic.base import TemplateView
from .views import join


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/join/', join, name='join'),
    path('accounts/', include("django.contrib.auth.urls")),
    path("membership/", include("membership.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="home")
]
