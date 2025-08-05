from django.shortcuts import render,redirect

# Create your views here
def home(request):
    return render(request,'index.html')
def login(request):
    return render(request,'login.html')
def logout(request):
    return redirect('/login')
def dashboard(request):
    return render(request,'student_dashboard.html')