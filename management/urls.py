from django.urls import path
from . import views

app_name = 'management'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('login_dashboard/', views.login_dashboard, name='login_dashboard'),
    path('forgot_password/', views.forgot_password_request, name='forgot_password_request'),
    path('reset_password/<str:token>/', views.reset_password, name='reset_password'),
    path('add_student/', views.add_student, name='add_student'),
    path('add_driver/', views.add_driver, name='add_driver'),
    path('add_management_personnel/', views.add_management_personnel, name='add_management_personnel'),
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    path('add_driver_csv/', views.add_driver_csv, name='add_driver_csv'),
    path('add_management_csv/', views.add_management_csv, name='add_management_csv'),
    path('take_action/', views.take_action, name='take_action'),
]
