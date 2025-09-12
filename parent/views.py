from django.shortcuts import render, redirect
from django.contrib import messages
from .models import parent, Complaint, PasswordResetToken
from student.models import student_details
from driver.models import Bus
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
import pytz
from datetime import datetime

# Create your views here.
def dashboard(request):
    if 'parent_user_id' not in request.session:
        return redirect('parent:login')
    parent_id = request.session['parent_user_id']
    students = student_details.objects.filter(parent_id=parent_id)
    complaints = Complaint.objects.filter(parent_id=parent_id).order_by('-created_at')[:10]  # Recent 10 complaints
    buses = Bus.objects.all()

    # Get boarding status for each student
    from driver.models import StudentBoarding
    from django.utils import timezone
    today = timezone.now().date()
    ist_tz = pytz.timezone('Asia/Kolkata')
    student_status = []
    for student in students:
        boarding = StudentBoarding.objects.filter(student=student, date=today).first()
        if boarding:
            status = boarding.status
            boarding_time = boarding.time
            if boarding_time:
                utc_dt = datetime.combine(today, boarding_time, tzinfo=pytz.utc)
                ist_dt = utc_dt.astimezone(ist_tz)
                boarding_time = ist_dt.time()
        else:
            status = 'not_boarded'
            boarding_time = None
        student_status.append({
            'student': student,
            'status': status,
            'boarding_time': boarding_time,
        })

    context = {
        'student_status': student_status,
        'complaints': complaints,
        'buses': buses,
    }
    return render(request, 'parent_dashboard.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = parent.objects.get(email=email)
            if check_password(password, user.password):
                request.session['parent_user_id'] = user.id
                request.session['parent_user_email'] = user.email
                request.session['parent_user_name'] = user.name
                return redirect('parent:dashboard')
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, 'parent_login.html')
        except parent.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'parent_login.html')
    else:
        return render(request, 'parent_login.html')

def logout(request):
    request.session.flush()
    return redirect('parent:login')

def login_dashboard(request):
    return redirect('/login_dashboard')

def submit_complaint(request):
    if 'parent_user_id' not in request.session:
        return redirect('parent:login')
    if request.method == 'POST':
        complaint_type = request.POST.get('complaintType')
        bus_id = request.POST.get('complaintBus')
        description = request.POST.get('complaintDescription')
        priority = request.POST.get('complaintPriority')
        parent_id = request.session['parent_user_id']
        try:
            parent_obj = parent.objects.get(id=parent_id)
            bus_obj = None
            if bus_id:
                from driver.models import Bus
                bus_obj = Bus.objects.get(id=bus_id)
            Complaint.objects.create(
                parent=parent_obj,
                complaint_type=complaint_type,
                bus=bus_obj,
                description=description,
                priority=priority
            )
            messages.success(request, 'Complaint submitted successfully!')
        except Exception as e:
            messages.error(request, 'Error submitting complaint.')
    return redirect('parent:dashboard')

def forgot_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = parent.objects.get(email=email)
            token = PasswordResetToken.objects.create(parent_user=user)
            reset_link = f"http://127.0.0.1:8000/parent/reset_password/{token.token}/"
            send_mail(
                'Password Reset Request',
                f'Hi {user.name},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn\'t request this, ignore this email.',
                'noreply@schoolbus.com',
                [user.email]
            )
            messages.success(request, 'Password reset link sent to your email')
        except parent.DoesNotExist:
            messages.error(request, 'Email not found')
    return render(request, 'forgot_password.html')

def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            messages.error(request, 'Token has expired')
            return redirect('parent:forgot_password_request')
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return redirect('parent:reset_password', token=token)
            user = reset_token.parent_user
            user.password = make_password(new_password)
            user.save()
            reset_token.delete()
            messages.success(request, 'Password reset successfully')
            return redirect('parent:login')
        return render(request, 'reset_password.html')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid token')
        return redirect('parent:forgot_password_request')
