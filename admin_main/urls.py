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
app_name='admin_main'
urlpatterns = [
    path('',views.dashboard,name="dashboard"),
    path("login/",views.login,name="login"),
    path('login_dashboard/', views.login_dashboard, name='login_dashboard'),
    path("logout/",views.logout,name="logout"),
    path('forgot_password/', views.forgot_password_request, name='forgot_password_request'),
    path('reset_password/<str:token>/', views.reset_password, name='reset_password'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('update_user/', views.update_user, name='update_user'),
]
