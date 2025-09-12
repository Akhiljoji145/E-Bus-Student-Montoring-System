"""
URL configuration for student_monitoring project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from . import views
app_name='driver'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('login_dashboard/', views.login_dashboard, name='login_dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout, name='logout'),
    path('mark_student_boarded/<int:student_id>/', views.mark_student_boarded, name='mark_student_boarded'),
    path('send_bus_change_message/', views.send_bus_change_message, name='send_bus_change_message'),
    path('validate_departure/', views.validate_departure, name='validate_departure'),
    path('unregistered_alert/', views.unregistered_alert, name='unregistered_alert'),
    path('generate_qr_code/<int:bus_id>/', views.generate_qr_code, name='generate_qr_code'),
]
