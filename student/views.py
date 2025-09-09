from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import student_details, student_complaints, hosteler_reg, PasswordResetToken
from driver.models import Bus, Busdriver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string

# Create your views here
def home(request):
    return render(request, 'index.html')

def logindashboard(request):
    return render(request, 'dashboard_login.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            student = student_details.objects.get(email=email)
            if check_password(password, student.password):
                bus = Bus.objects.all()
                complaints = student_complaints.objects.all()
                hosteler_registration = hosteler_reg.objects.all()
                request.session['student_id'] = student.id
                request.session['student_name'] = student.name
                request.session['student_email'] = student.email
                request.session['student_class'] = student.stud_class
                request.session['student_branch'] = student.branch
                request.session['accommodation_type'] = student.accommodation_type
                return render(request, 'student_dashboard.html', {'student': student, 'bus': bus, 'complaints': complaints, 'hosteler_reg': hosteler_registration})
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, 'student_login.html')
        except student_details.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'student_login.html')
    return render(request, 'student_login.html')

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

def submit_complaint(request):
    if request.method == "POST":
        student_id = request.POST.get('id')
        bus = request.POST.get('bus_id')
        comp = request.POST.get('complaint')
        complaints = student_complaints(student_id=student_id, bus=bus, complaint=comp)
        complaints.save()
        return redirect('/dashboard')

def dashboard(request):
    if 'student_id' in request.session:
        student_id = request.session['student_id']
        student = student_details.objects.get(id=student_id)
        if student.password == '':
            messages.info(request, 'Please update your password')
            return redirect('/update_password')
        bus = Bus.objects.all()
        complaints = student_complaints.objects.all()
        hosteler_registration = hosteler_reg.objects.all()
        # Check existing bus registrations
        
        return render(request, 'student_dashboard.html', {
            'student': student,
            'bus': bus,
            'complaints': complaints,
            'hosteler_reg': hosteler_registration,
        })
    else:
        return redirect('/login')

def bus_registration(request):
    if request.method == 'POST':
        student = request.session['student_id']
        student_instance = student_details.objects.get(id=student)
        bus_time = request.POST.get('bus_time')
        pickup_point = request.POST.get('pickup_point')
        bus = request.POST.get('bus')
        bus_instance = Bus.objects.get(bus_no=bus)
        bus_no = bus_instance.bus_no
        reg = hosteler_reg(student_id=student_instance, pickup_time=bus_time, pickup_point=pickup_point, bus=bus_instance, status='Pending')
        reg.save()
        return redirect('/dashboard')

def delete_registration(request, registration_id):
    if request.method == 'DELETE':
        try:
            registration = hosteler_reg.objects.get(id=registration_id)
            registration.delete()
            return JsonResponse({'status': 'success', 'message': 'Registration deleted successfully'})
        except hosteler_reg.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Registration not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def update_password(request):
    # This view is for logged-in users to update their password
    if 'student_id' in request.session:
        student_id = request.session['student_id']
        student = student_details.objects.get(id=student_id)
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password == confirm_password:
                student.password = make_password(new_password)
                student.save()
                messages.success(request, 'Password updated successfully')
                return redirect('/dashboard')
            else:
                messages.error(request, 'Passwords do not match')
                return render(request, 'student_password.html', {'student': student})
        return render(request, 'student_password.html', {'student': student})
    else:
        return redirect('/login')

def forgot_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = student_details.objects.get(email=email)
            # Create a password reset token
            token_obj = PasswordResetToken.objects.create(student=user)
            reset_link = request.build_absolute_uri(f"/reset_password/{token_obj.token}/")
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
                return redirect('student:login')
            except Exception as e:
                # Log the error and inform the user
                print(f"Error sending email: {e}")  # For debugging
                messages.error(request, 'There was an error sending the email. Please try again later.')
                return render(request, 'forgot_password.html')
        except student_details.DoesNotExist:
            messages.error(request, 'Email address not found.')
            return render(request, 'forgot_password.html')
    return render(request, 'forgot_password.html')

def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset token.')
        return redirect('student:forgot_password_request')

    if not token_obj.is_valid():
        messages.error(request, 'Password reset token has expired.')
        return redirect('student:forgot_password_request')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            user = token_obj.student
            user.password = make_password(new_password)
            user.save()
            token_obj.delete()  # Invalidate token after use
            messages.success(request, 'Password has been reset successfully.')
            return redirect('student:login')
        else:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'reset_password.html', {'token': token})
    return render(request, 'reset_password.html', {'token': token})
