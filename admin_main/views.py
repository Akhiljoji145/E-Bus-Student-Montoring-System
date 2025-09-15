from django.shortcuts import render,redirect
from django.contrib import messages
from .models import admin_main, PasswordResetToken
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from student.models import student_details, student_complaints
from parent.models import parent, Complaint
from driver.models import Busdriver
from teacher.models import teacher, MissingStudentAlert
from management.models import management

# Create your views here.
def dashboard(request):
    # Check if admin user is logged in
    if not request.session.get('admin_user_id'):
        return redirect('admin_main:login')

    # Fetch all users from different roles
    students = student_details.objects.all()
    parents = parent.objects.all()
    teachers = teacher.objects.all()
    drivers = Busdriver.objects.all()
    managements = management.objects.all()

    # Combine users into a list of dicts for template
    users = []
    for s in students:
        users.append({'id': f'student-{s.id}', 'name': s.name, 'role': 'Student'})
    for p in parents:
        users.append({'id': f'parent-{p.id}', 'name': p.name, 'role': 'Parent'})
    for t in teachers:
        users.append({'id': f'teacher-{t.id}', 'name': t.teacher_name, 'role': 'Teacher'})
    for d in drivers:
        users.append({'id': f'driver-{d.id}', 'name': d.bus_driver, 'role': 'Driver'})
    for m in managements:
        users.append({'id': f'management-{m.id}', 'name': m.name, 'role': 'Management'})

    # Fetch complaints from parent and student apps, and missing alerts
    parent_complaints = Complaint.objects.all()
    student_complaints_list = student_complaints.objects.all()
    missing_alerts = MissingStudentAlert.objects.filter(status='active')

    # Combine complaints and alerts for template
    complaints = []
    for c in parent_complaints:
        complaints.append({
            'id': f'parent-{c.id}',
            'description': c.description,
            'from_user': f"Parent ({c.parent.name})",
            'action_taken': c.status,
            'date': c.created_at
        })
    for c in student_complaints_list:
        complaints.append({
            'id': f'student-{c.id}',
            'description': c.complaint,
            'from_user': f"Student ({c.complaint_by})",
            'action_taken': c.action_taken,
            'date': c.date
        })
    for a in missing_alerts:
        complaints.append({
            'id': f'missing-{a.id}',
            'description': f"Missing Student Alert: {a.student_name} - {a.bus_route} - {a.last_seen}",
            'from_user': f"Teacher ({a.reported_by.teacher_name})",
            'action_taken': a.status,
            'date': a.reported_at
        })

    # Sort complaints by date descending (most recent first)
    complaints.sort(key=lambda x: x['date'], reverse=True)

    # Get bus messages for school admin
    from driver.models import BusMessage
    bus_messages = BusMessage.objects.filter(audience='school_admin').order_by('-sent_at')

    context = {
        'users': users,
        'complaints': complaints,
        'admin_name': request.session.get('admin_user_name'),
        'bus_messages': bus_messages,
    }
    return render(request, 'admin_dashboard.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = admin_main.objects.get(email=email)
            if check_password(password, user.password):
                request.session['admin_user_id'] = user.id
                request.session['admin_user_email'] = user.email
                request.session['admin_user_name'] = user.name
                return redirect('admin_main:dashboard')
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, 'admin_main_login.html')
        except admin_main.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'admin_main_login.html')
    else:
        return render(request, 'admin_main_login.html')

def logout(request):
    request.session.flush()
    return redirect('admin_main:login')

def login_dashboard(request):
    return redirect('/login_dashboard')

def forgot_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = admin_main.objects.get(email=email)
            # Create a password reset token
            token_obj = PasswordResetToken.objects.create(admin_user=user)
            reset_link = request.build_absolute_uri(f"/admin_main/reset_password/{token_obj.token}/")
            # Render HTML email
            html_message = render_to_string('password_reset_email.html', {
                'user_name': user.name,
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
                return redirect('admin_main:login')
            except Exception as e:
                # Log the error and inform the user
                print(f"Error sending email: {e}")  # For debugging
                messages.error(request, 'There was an error sending the email. Please try again later.')
                return render(request, 'management_forgot_password.html')
        except admin_main.DoesNotExist:
            messages.error(request, 'Email address not found.')
            return render(request, 'management_forgot_password.html')
    return render(request, 'management_forgot_password.html')

def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset token.')
        return redirect('admin_main:forgot_password_request')

    if not token_obj.is_valid():
        messages.error(request, 'Password reset token has expired.')
        return redirect('admin_main:forgot_password_request')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            user = token_obj.admin_user
            user.password = make_password(new_password)
            user.save()
            token_obj.delete()  # Invalidate token after use
            messages.success(request, 'Password has been reset successfully.')
            return redirect('admin_main:login')
        else:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'management_reset_password.html', {'token': token})
    return render(request, 'management_reset_password.html', {'token': token})

def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not user_id:
            return JsonResponse({'success': False, 'error': 'No user_id provided'})
        try:
            user_type, id_str = user_id.split('-')
            id = int(id_str)
        except Exception:
            return JsonResponse({'success': False, 'error': 'Invalid user_id format'})
        try:
            if user_type == 'student':
                student_details.objects.get(id=id).delete()
            elif user_type == 'parent':
                parent.objects.get(id=id).delete()
            elif user_type == 'driver':
                Busdriver.objects.get(id=id).delete()
            elif user_type == 'teacher':
                teacher.objects.get(id=id).delete()
            elif user_type == 'management':
                management.objects.get(id=id).delete()
            else:
                return JsonResponse({'success': False, 'error': 'Unknown user type'})
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def update_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        # Placeholder for update logic
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
