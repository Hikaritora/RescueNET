"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from management.views import lista_incydentow
from management.views import nowy_incydent
from management.views import lista_zasobow
from management.views import przypisz_zasob
from django.contrib.auth import views as auth_views
from management.views import zakoncz_incydent
from management.views import szczegoly_incydentu
from management.views import dashboard
from management.views import archiwum_incydentow
from management.views import eksportuj_raport
from management.views import dodaj_zasob
from management.views import usun_przypisanie_zasobu

urlpatterns = [
    path('admin/', admin.site.urls),
    path('incydenty/', lista_incydentow, name='lista_incydentow'), # Nowy adres 
    path('nowy/', nowy_incydent, name='nowy_incydent'),
    path('zasoby/', lista_zasobow, name='lista_zasobow'),
    path('zasoby/assign/<int:zasob_id>/', przypisz_zasob, name='przypisz_zasob'),
    path('login/', auth_views.LoginView.as_view(template_name='management/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('incydenty/<int:pk>/zakoncz/', zakoncz_incydent, name='zakoncz_incydent'),
    path('incydenty/<int:pk>/', szczegoly_incydentu, name='szczegoly_incydentu'),
    path('', dashboard, name='dashboard'),
    path('archiwum/', archiwum_incydentow, name='archiwum'),
    path('archiwum/export/', eksportuj_raport, name='eksport_csv'),
    path('zasob/dodaj/', dodaj_zasob, name='dodaj_zasob'),
    path('incydenty/<int:pk>/usun-zasob/<int:zasob_id>/', usun_przypisanie_zasobu, name='usun_przypisanie_zasobu'),
]