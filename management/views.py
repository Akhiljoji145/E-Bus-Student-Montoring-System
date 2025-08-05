from django.shortcuts import render

# Create your views here.
def dashboard(request):
    return render(request,'management_dashboard.html')