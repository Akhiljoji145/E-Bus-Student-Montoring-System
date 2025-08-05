from django.shortcuts import render, redirect


# Create your views here.
def dashboard(request):
    return render(request,'driver_dashboard.html')
def logout(request):
    return redirect('/login')