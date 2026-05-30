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
from management.views import list_incidents
from management.views import create_incident
from management.views import list_resources
from management.views import assign_resource
from django.contrib.auth import views as auth_views
from management.views import close_incident
from management.views import incident_detail
from management.views import dashboard
from management.views import archive
from management.views import export_report
from management.views import add_resource
from management.views import unassign_resource
from management.views import delete_resource

urlpatterns = [
    path('admin/', admin.site.urls),
    path('incidents/', list_incidents, name='incident_list'),
    path('incidents/create/', create_incident, name='create_incident'),
    path('resources/', list_resources, name='resource_list'),
    path('resources/assign/<int:zasob_id>/', assign_resource, name='assign_resource'),
    path('login/', auth_views.LoginView.as_view(template_name='management/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('incidents/<int:pk>/close/', close_incident, name='close_incident'),
    path('incidents/<int:pk>/', incident_detail, name='incident_detail'),
    path('', dashboard, name='dashboard'),
    path('archive/', archive, name='archive'),
    path('archive/export/', export_report, name='export_csv'),
    path('resource/add/', add_resource, name='add_resource'),
    path('resource/delete/<int:zasob_id>/', delete_resource, name='delete_resource'),
    path('incidents/<int:pk>/unassign-resource/<int:zasob_id>/', unassign_resource, name='unassign_resource'),
]


