from django.shortcuts import render,redirect
from django.contrib import messages
from .models import student_details

# Create your views here
def home(request):
    return render(request,'index.html')
def logindashboard(request):
    return render(request,'dashboard_login.html')
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            student = student_details.objects.get(email=email, password=password)
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            request.session['student_email'] = student.email
            request.session['student_class'] = student.stud_class
            request.session['student_branch'] = student.branch
            request.session['accommodation_type'] = student.accommodation_type
            
            return redirect('/dashboard/')
        except student_details.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'student_login.html')
    
    return render(request,'student_login.html')

def logout(request):
    # Clear session
    if 'student_id' in request.session:
        del request.session['student_id']
    if 'student_name' in request.session:
        del request.session['student_name']
    if 'student_email' in request.session:
        del request.session['student_email']
    if 'student_class' in request.session:
        del request.session['student_class']
    if 'student_branch' in request.session:
        del request.session['student_branch']
    if 'accommodation_type' in request.session:
        del request.session['accommodation_type']
    
    return redirect('/login')

def dashboard(request):
    # Check if student is logged in
    if 'student_id' not in request.session:
        return redirect('/login')
    
    # Create context with session data
    context = {
        'student_name': request.session.get('student_name'),
        'student_email': request.session.get('student_email'),
        'student_class': request.session.get('student_class'),
        'student_branch': request.session.get('student_branch'),
        'accommodation_type': request.session.get('accommodation_type'),
    }
    
    return render(request,'student_dashboard.html')
