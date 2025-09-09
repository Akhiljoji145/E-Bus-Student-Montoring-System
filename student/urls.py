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
app_name='student'
urlpatterns = [
    path("",views.home,name="home"),
    path("login_dashboard/",views.logindashboard,name="login_dashboard"),
    path("login/",views.login,name="login"),
    path("logout/",views.logout,name="logout"),
    path("complaint/",views.submit_complaint,name="complaint"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("hosteler_reg/",views.bus_registration,name="hosteler_registration"),
    path("delete-registration/<int:registration_id>/", views.delete_registration, name="delete_registration"),
    path("update_password/",views.update_password,name="update_password"),
    path("forgot_password/", views.forgot_password_request, name="forgot_password_request"),
    path("reset_password/<uuid:token>/", views.reset_password, name="reset_password"),
]
