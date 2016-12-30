"""sixsevenba URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from chinesestory import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^$', views.adminlogin),
	url(r'^chinesestory/$', views.index),
	url(r'^chinesestory/admin/', views.adminlogin),
	url(r'^chinesestory/logout/', views.adminlogout),
	url(r'^chinesestory/brossard/$', views.shownotice),
	url(r'^chinesestory/brossard/registration/', views.registration),
	url(r'^chinesestory/longueuil/$', views.shownotice),
	url(r'^chinesestory/longueuil/registration/', views.registration),
	url(r'^chinesestory/montreal/$', views.shownotice),
	url(r'^chinesestory/montreal/registration/', views.registration),
	url(r'^chinesestory/createnotice/', views.createnotice),
	url(r'^chinesestory/viewregistration/', views.viewregistration),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
