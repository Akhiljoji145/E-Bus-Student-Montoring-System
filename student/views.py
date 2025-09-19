from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import student_details, student_complaints, hosteler_reg, PasswordResetToken
from driver.models import Bus, Busdriver, StudentBoarding
from teacher.models import teacher
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
import pytz
from datetime import datetime
def index(request):
    return render(request, 'index.html')
def home(request):
    return redirect('student:login_dashboard')

def login_dashboard(request):
    return render(request, 'dashboard_login.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            student = student_details.objects.get(email=email)
            if check_password(password, student.password):
                request.session['student_id'] = student.id
                request.session['student_name'] = student.name
                return redirect('student:dashboard')
            else:
                messages.error(request, 'Invalid email or password')
        except student_details.DoesNotExist:
            messages.error(request, 'Invalid email or password')
    return render(request, 'student_login.html')

def logout(request):
    request.session.flush()
    return redirect('student:login')

def bus_registration(request):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        bus_id = request.POST.get('bus_id')
        pickup_time = request.POST.get('pickup_time')
        pickup_point = request.POST.get('pickup_point')
        if student_id and bus_id and pickup_time and pickup_point:
            from .models import hosteler_reg
            from driver.models import Bus
            try:
                student = student_details.objects.get(id=student_id)
                bus = Bus.objects.get(id=bus_id)
                hosteler_reg.objects.create(
                    student_id=student,
                    bus=bus,
                    pickup_time=pickup_time,
                    pickup_point=pickup_point,
                    status='registered'
                )
                messages.success(request, 'Bus registration successful')
            except Exception as e:
                messages.error(request, f'Error during registration: {str(e)}')
        else:
            messages.error(request, 'Please fill in all fields')
        return redirect('student:dashboard')
    else:
        from driver.models import Bus
        buses = Bus.objects.all()
        return render(request, 'hosteler_registration.html', {'buses': buses})

def dashboard(request):
    if 'student_id' not in request.session:
        return redirect('student:login')
    student_id = request.session['student_id']
    student = student_details.objects.get(id=student_id)
    context = {
        'student': student,
    }
    return render(request, 'student_dashboard.html', context)

def submit_complaint(request):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        complaint = request.POST.get('complaint')
        bus = request.POST.get('bus')
        if student_id and complaint:
            student_complaints.objects.create(
                student_id=student_id,
                complaint=complaint,
                bus=bus
            )
            messages.success(request, 'Complaint submitted successfully')
        else:
            messages.error(request, 'Please fill in all fields')
    return redirect('student:dashboard')

def delete_registration(request, registration_id):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        try:
            registration = hosteler_reg.objects.get(id=registration_id, student_id_id=student_id)
            registration.delete()
            messages.success(request, 'Registration deleted successfully')
        except hosteler_reg.DoesNotExist:
            messages.error(request, 'Registration not found')
    return redirect('student:dashboard')

def update_password(request):
    if request.method == 'POST':
        student_id = request.session.get('student_id')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match')
            return redirect('student:update_password')
        try:
            student = student_details.objects.get(id=student_id)
            if check_password(old_password, student.password):
                student.password = make_password(new_password)
                student.save()
                messages.success(request, 'Password updated successfully')
            else:
                messages.error(request, 'Old password is incorrect')
        except student_details.DoesNotExist:
            messages.error(request, 'Student not found')
    return redirect('student:dashboard')

def forgot_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            student = student_details.objects.get(email=email)
            token = PasswordResetToken.objects.create(student=student)
            reset_link = f"http://127.0.0.1:8000/student/reset_password/{token.token}/"
            send_mail(
                'Password Reset Request',
                f'Hi {student.name},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn\'t request this, ignore this email.',
                'noreply@schoolbus.com',
                [student.email]
            )
            messages.success(request, 'Password reset link sent to your email')
        except student_details.DoesNotExist:
            messages.error(request, 'Email not found')
    return render(request, 'forgot_password.html')

def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            messages.error(request, 'Token has expired')
            return redirect('student:forgot_password_request')
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match')
                return redirect('student:reset_password', token=token)
            student = reset_token.student
            student.password = make_password(new_password)
            student.save()
            reset_token.delete()
            messages.success(request, 'Password reset successfully')
            return redirect('student:login')
        return render(request, 'reset_password.html')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid token')
        return redirect('student:forgot_password_request')

# Existing views omitted for brevity...

def qr_scan(request):
    # Render the QR code scanning interface page
    student_id = request.session.get('student_id')
    return render(request, 'qr_scan.html', {'student_id': student_id})

@csrf_exempt
def handle_boarding(request, bus_id):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if not student_id or not student_id.isdigit():
            return JsonResponse({'status': 'error', 'message': 'Invalid student ID'})
        try:
            student = student_details.objects.get(id=int(student_id))
            bus = Bus.objects.get(id=bus_id)
            today = timezone.now().date()
            current_time = timezone.now().time()
            ist_tz = pytz.timezone('Asia/Kolkata')
            current_time_ist = timezone.now().astimezone(ist_tz).time()

            # Define scanning time windows
            morning_start = datetime.strptime('05:00:00', '%H:%M:%S').time()
            morning_end = datetime.strptime('12:00:00', '%H:%M:%S').time()
            evening_start = datetime.strptime('15:00:00', '%H:%M:%S').time()
            evening_end = datetime.strptime('20:00:00', '%H:%M:%S').time()

            # Check if current time is within allowed scanning windows
            if morning_start <= current_time_ist <= morning_end:
                is_morning_scan = True
            elif evening_start <= current_time_ist <= evening_end:
                is_morning_scan = False
            else:
                return JsonResponse({'status': 'error', 'message': 'Scanning not allowed at this time'})

            # Check if student is registered for this bus (day scholar or hosteler)
            is_registered = student.bus == bus or hosteler_reg.objects.filter(student_id=student, bus=bus.bus_no).exists()

            if is_registered:
                # Get or create boarding record for today
                boarding, created = StudentBoarding.objects.get_or_create(
                    student=student,
                    bus=bus,
                    date=today,
                )
                if is_morning_scan:
                    boarding.morning_scan = True
                    if latitude and longitude:
                        boarding.morning_latitude = latitude
                        boarding.morning_longitude = longitude
                else:
                    boarding.evening_scan = True
                    if latitude and longitude:
                        boarding.evening_latitude = latitude
                        boarding.evening_longitude = longitude

                boarding.status = 'boarded'
                boarding.time = timezone.now().time()
                boarding.save()

                message = f'You are boarded successfully for {"morning" if is_morning_scan else "evening"} session'

                # Send alert to teachers related to student's class and branch
                related_teachers = teacher.objects.filter(class_no=student.stud_class, branch=student.branch)
                for t in related_teachers:
                    pass  # Placeholder for future alert logic if needed
                return JsonResponse({'status': 'success', 'message': message})
            else:
                # Student not registered for this bus
                return JsonResponse({'status': 'error', 'message': 'Student not registered for this bus'})
        except student_details.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student not found'})
        except Bus.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Bus not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
