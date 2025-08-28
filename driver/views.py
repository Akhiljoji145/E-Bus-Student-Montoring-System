from django.shortcuts import render, redirect
from .models import Busdriver,Bus
from student.models import hosteler_reg,student_details
# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            busdriver_login = Busdriver.objects.get(email=email, password=password)
            bus= Bus.objects.all()
            request.session['id'] = busdriver_login.id
            request.session['bus_driver'] = busdriver_login.bus_driver
            request.session['email'] = busdriver_login.email
            request.session['bus_id'] = busdriver_login.bus_id
            return render(request,'driver_dashboard.html',{'driver':busdriver_login,'bus':bus,'hosteler_reg':hosteler_registration})
        except student_details.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'student_login.html')
    return render(request,'_login.html')