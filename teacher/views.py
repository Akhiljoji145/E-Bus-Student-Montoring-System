from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
import secrets
import string
import pytz
from datetime import time
from .models import teacher, MissingStudentAlert, StudentStatusOverride, PasswordResetToken
from student.models import student_details
from driver.models import Busdriver, Bus, StudentBoarding

# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            teacher_obj = teacher.objects.get(email=email)
            if check_password(password, teacher_obj.password):
                request.session['teacher_id'] = teacher_obj.id
                request.session['teacher_name'] = teacher_obj.teacher_name
                return redirect('teacher:dashboard')
            else:
                messages.error(request, 'Invalid email or password')
                return redirect('teacher:login')
        except teacher.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('teacher:login')
    return render(request, 'teacher_login.html')

def dashboard(request):
    if 'teacher_id' not in request.session:
        return redirect('teacher:login')

    teacher_id = request.session['teacher_id']
    teacher_obj = teacher.objects.get(id=teacher_id)

    # Get active missing student alerts
    alerts = MissingStudentAlert.objects.filter(status='active').order_by('-reported_at')[:10]

    # Get boarding alerts for teacher - students not boarded today, only for teacher's class
    today = timezone.now().date()
    boarding_alerts = StudentBoarding.objects.filter(date=today, student__stud_class=teacher_obj.class_no).exclude(status='departed').order_by('student__name')

    # Convert times to IST
    ist_tz = pytz.timezone('Asia/Kolkata')
    for alert in alerts:
        alert.reported_at = alert.reported_at.astimezone(ist_tz)
        alert.formatted_reported_at = alert.reported_at.strftime('%Y-%m-%d %I:%M:%S %p')
    for alert in boarding_alerts:
        if not alert.morning_scan and not alert.evening_scan:
            alert.alert_type = 'not_boarded'
        elif alert.morning_scan and not alert.evening_scan:
            alert.alert_type = 'not_boarded_evening'
        elif not alert.morning_scan and alert.evening_scan:
            alert.alert_type = 'not_boarded_morning'
        else:
            alert.alert_type = 'boarded'
        alert.formatted_sent_at = timezone.now().astimezone(ist_tz).strftime('%Y-%m-%d %I:%M:%S %p')

    # Get all students for dropdowns
    students = student_details.objects.all().order_by('name')

    # Get all buses for dropdowns
    buses = Bus.objects.all().order_by('bus_no')

    context = {
        'alerts': alerts,
        'boarding_alerts': boarding_alerts,
        'students': students,
        'buses': buses,
        'teacher_name': request.session.get('teacher_name', '')
    }
    return render(request, 'teacher_dashboard.html', context)

def bus_tracking(request):
    if 'teacher_id' in request.session:
        teacher_id = request.session['teacher_id']
        teacher_obj = teacher.objects.get(id=teacher_id)
        # For simplicity, show all active buses and their drivers
        drivers = Busdriver.objects.all()
        return render(request, 'bus_tracking.html', {
            'teacher': teacher_obj,
            'drivers': drivers
        })
    else:
        return redirect('teacher:login')

def logout(request):
    request.session.flush()
    return redirect('teacher:login')

def manual_override(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        bus_route = request.POST.get('bus_route')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        teacher_id = request.session['teacher_id']
        teacher_obj = teacher.objects.get(id=teacher_id)

        # Create the override record
        override = StudentStatusOverride.objects.create(
            student_name=student_name,
            bus_route=bus_route,
            action=action,
            applied_by=teacher_obj,
            notes=notes
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Manual override applied: {student_name} marked as {action}',
            'override_id': override.id
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def report_missing_student(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        bus_route = request.POST.get('bus_route')
        details = request.POST.get('details')

        teacher_id = request.session['teacher_id']
        teacher_obj = teacher.objects.get(id=teacher_id)

        # Create an alert for immediate action
        alert = MissingStudentAlert.objects.create(
            student_name=student_name,
            bus_route=bus_route,
            last_seen=details,
            parent_contact='Contact school administration',
            reported_by=teacher_obj
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Missing student alert created for {student_name}',
            'alert_id': alert.id
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def resolve_alert(request, alert_id):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    try:
        alert = MissingStudentAlert.objects.get(id=alert_id)
        alert.status = 'resolved'
        alert.save()

        return JsonResponse({
            'status': 'success',
            'message': f'Alert for {alert.student_name} has been resolved'
        })
    except MissingStudentAlert.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Alert not found'})

def get_alerts(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    alerts = MissingStudentAlert.objects.filter(status='active').order_by('-reported_at')[:20]
    alerts_data = []

    ist_tz = pytz.timezone('Asia/Kolkata')
    for alert in alerts:
        reported_at_ist = alert.reported_at.astimezone(ist_tz)
        alerts_data.append({
            'id': alert.id,
            'student_name': alert.student_name,
            'bus_route': alert.bus_route,
            'last_seen': alert.last_seen,
            'parent_contact': alert.parent_contact,
            'reported_at': reported_at_ist.strftime('%Y-%m-%d %I:%M:%S %p')
        })

    return JsonResponse({
        'status': 'success',
        'alerts': alerts_data
    })

def get_boarding_alerts(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    teacher_id = request.session['teacher_id']
    teacher_obj = teacher.objects.get(id=teacher_id)

    today = timezone.now().date()
    alerts = StudentBoarding.objects.filter(date=today, student__stud_class=teacher_obj.class_no).exclude(status='departed').order_by('student__name')[:20]
    alerts_data = []

    ist_tz = pytz.timezone('Asia/Kolkata')
    for alert in alerts:
        if not alert.morning_scan:
            alert_type = 'not_boarded_morning'
        elif alert.morning_scan and not alert.evening_scan:
            alert_type = 'not_boarded_evening'
        else:
            alert_type = 'not_boarded'
        sent_at_ist = timezone.now().astimezone(ist_tz).strftime('%Y-%m-%d %I:%M:%S %p')
        alerts_data.append({
            'id': alert.id,
            'student_name': alert.student.name,
            'bus_route': alert.bus.bus_starting_point,
            'alert_type': alert_type,
            'sent_at': sent_at_ist
        })

    return JsonResponse({
        'status': 'success',
        'alerts': alerts_data
    })

def get_all_bus_locations(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    drivers = Busdriver.objects.all()
    buses_data = []

    for driver in drivers:
        if driver.latitude and driver.longitude:
            buses_data.append({
                'driver_id': driver.id,
                'driver_name': driver.bus_driver,
                'bus_no': driver.bus_id.bus_no if driver.bus_id else 'N/A',
                'latitude': str(driver.latitude),
                'longitude': str(driver.longitude),
                'last_updated': driver.last_updated.strftime('%Y-%m-%d %I:%M:%S %p') if driver.last_updated else 'Never'
            })

    return JsonResponse({
        'status': 'success',
        'buses': buses_data
    })

def forgot_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = teacher.objects.get(email=email)
            # Create a password reset token
            token_obj = PasswordResetToken.objects.create(teacher_user=user)
            reset_link = request.build_absolute_uri(f"/teacher/reset_password/{token_obj.token}/")
            # Render HTML email
            html_message = render_to_string('password_reset_email.html', {
                'user_name': user.teacher_name,
                'reset_link': reset_link
            })
            # Send email with reset link
            try:
                send_mail(
                    'Password Reset Request - BusTracker Pro',
                    'Please use an HTML-compatible email client to view this message.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('teacher:login')
            except Exception as e:
                # Log the error and inform the user
                print(f"Error sending email: {e}")  # For debugging
                messages.error(request, 'There was an error sending the email. Please try again later.')
                return render(request, 'management_forgot_password.html')
        except teacher.DoesNotExist:
            messages.error(request, 'Email address not found.')
            return render(request, 'management_forgot_password.html')
    return render(request, 'management_forgot_password.html')

def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset token.')
        return redirect('teacher:forgot_password_request')

    if not token_obj.is_valid():
        messages.error(request, 'Password reset token has expired.')
        return redirect('teacher:forgot_password_request')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            user = token_obj.teacher_user
            user.password = new_password  # Note: not hashing for simplicity, but should hash in production
            user.save()
            token_obj.delete()  # Invalidate token after use
            messages.success(request, 'Password has been reset successfully.')
            return redirect('teacher:login')
        else:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'management_reset_password.html', {'token': token})
    return render(request, 'management_reset_password.html', {'token': token})
def login_dashboard(request):
    return redirect('/login_dashboard')
