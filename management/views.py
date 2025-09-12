from django.shortcuts import render, redirect
from django.contrib import messages
from .models import management, PasswordResetToken
from student.models import student_details, student_complaints
from driver.models import Busdriver, Bus
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
import secrets
import string




def generate_random_password(length=8):
    """Generate a random password with letters, digits, and special characters"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password



from teacher.models import teacher

def dashboard(request):
    if request.session.get('management_user_id'):
        # Get summary data
        total_students = student_details.objects.count()
        total_drivers = Busdriver.objects.count()
        total_buses = Bus.objects.count()
        total_teachers = teacher.objects.count()
        total_complaints = student_complaints.objects.count()
        pending_complaints = student_complaints.objects.filter(status__in=['', 'pending']).count()

        # Get recent complaints
        recent_complaints = student_complaints.objects.order_by('-date')[:5]

        # Get bus status overview
        buses = Bus.objects.all()
        bus_status = []
        for bus in buses:
            driver_count = Busdriver.objects.filter(bus_id=bus).count()
            student_count = student_details.objects.filter(bus=bus).count()
            complaint_count = student_complaints.objects.filter(bus=str(bus.bus_no)).count()
            bus_status.append({
                'bus_no': bus.bus_no,
                'starting_point': bus.bus_starting_point,
                'drivers': driver_count,
                'students': student_count,
                'complaints': complaint_count
            })

        context = {
            'total_students': total_students,
            'total_drivers': total_drivers,
            'total_buses': total_buses,
            'total_teachers': total_teachers,
            'total_complaints': total_complaints,
            'pending_complaints': pending_complaints,
            'recent_complaints': recent_complaints,
            'bus_status': bus_status,
            'bus': buses,
            'user_name': request.session.get('management_user_name', 'Management User')
        }
        return render(request, 'management_dashboard.html', context)
    else:
        return redirect('management:login')

def take_action(request):
    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        action_taken = request.POST.get('action_taken')
        try:
            complaint = student_complaints.objects.get(id=complaint_id)
            complaint.action_taken = action_taken
            complaint.status = 'resolved'
            complaint.save()
            messages.success(request, 'Action taken and complaint marked as resolved.')
        except student_complaints.DoesNotExist:
            messages.error(request, 'Complaint not found.')
        return redirect('management:dashboard')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = management.objects.get(email=email)
            if check_password(password, user.password):
                request.session['management_user_id'] = user.id
                request.session['management_user_email'] = user.email
                request.session['management_user_name'] = user.name
                return redirect('management:dashboard')
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, 'management_login.html')
        except management.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'management_login.html')
    else:
        return render(request, 'management_login.html')

def logout(request):
    request.session.flush()
    return redirect('management:login')

def login_dashboard(request):
    return redirect('/login_dashboard')

def forgot_password_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = management.objects.get(email=email)
            # Create a password reset token
            token_obj = PasswordResetToken.objects.create(management_user=user)
            reset_link = request.build_absolute_uri(f"/management/reset_password/{token_obj.token}/")
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
                return redirect('management:login')
            except Exception as e:
                # Log the error and inform the user
                print(f"Error sending email: {e}")  # For debugging
                messages.error(request, 'There was an error sending the email. Please try again later.')
                return render(request, 'management_forgot_password.html')
        except management.DoesNotExist:
            messages.error(request, 'Email address not found.')
            return render(request, 'management_forgot_password.html')
    return render(request, 'management_forgot_password.html')

def reset_password(request, token):
    try:
        token_obj = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid or expired password reset token.')
        return redirect('management:forgot_password_request')

    if not token_obj.is_valid():
        messages.error(request, 'Password reset token has expired.')
        return redirect('management:forgot_password_request')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if new_password == confirm_password:
            user = token_obj.management_user
            user.password = make_password(new_password)
            user.save()
            token_obj.delete()  # Invalidate token after use
            messages.success(request, 'Password has been reset successfully.')
            return redirect('management:login')
        else:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'management_reset_password.html', {'token': token})
    return render(request, 'management_reset_password.html', {'token': token})

def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_no = request.POST.get('phone_no')
        stud_class = request.POST.get('stud_class')
        branch = request.POST.get('branch')
        accommodation_type = request.POST.get('accommodation_type')
        bus_id = request.POST.get('bus')

        # Check if email already exists
        if student_details.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists'})

        bus = None
        if bus_id:
            try:
                bus = Bus.objects.get(id=bus_id)
            except Bus.DoesNotExist:
                pass

        # If password is empty or None, generate a random password
        if not password:
            password = generate_random_password()

        # Hash the password before saving
        hashed_password = make_password(password)

        student = student_details(
            name=name,
            email=email,
            password=hashed_password,
            phone_no=phone_no,
            stud_class=stud_class,
            branch=branch,
            accommodation_type=accommodation_type,
            bus=bus
        )
        student.save()

        response_data = {
            'status': 'success',
            'message': 'Student added successfully',
            'student_email': email
        }

        return JsonResponse(response_data)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def add_driver(request):
    if request.method == 'POST':
        bus_driver = request.POST.get('bus_driver')
        email = request.POST.get('email')
        password = request.POST.get('password')
        ph_no = request.POST.get('ph_no')
        bus_id = request.POST.get('bus_id')
        status = request.POST.get('status', 'permanent')
        bus_photo = request.FILES.get('bus_photo')

        # Check if email already exists
        if Busdriver.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists'})

        bus = None
        if bus_id:
            try:
                bus = Bus.objects.get(id=bus_id)
            except Bus.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Bus not found'})

        driver = Busdriver(
            bus_driver=bus_driver,
            email=email,
            password=make_password(password),
            ph_no=ph_no,
            bus_id=bus,
            status=status,
            bus_photo=bus_photo
        )
        driver.save()
        return JsonResponse({'status': 'success', 'message': 'Driver added successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def add_management_personnel(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_no = request.POST.get('phone_no')

        # Check if email already exists
        if management.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists'})

        mgmt_personnel = management(
            name=name,
            email=email,
            password=make_password(password),
            phone_no=phone_no
        )
        mgmt_personnel.save()
        return JsonResponse({'status': 'success', 'message': 'Management personnel added successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def add_teacher(request):
    if request.method == 'POST':
        teacher_name = request.POST.get('teacher_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        class_no = request.POST.get('class_no')
        branch = request.POST.get('branch')
        sem = request.POST.get('sem')

        from teacher.models import teacher

        # Check if email already exists
        if teacher.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already exists'})

        new_teacher = teacher(
            teacher_name=teacher_name,
            email=email,
            password=password,
            class_no=class_no,
            branch=branch,
            sem=sem
        )
        new_teacher.save()
        return JsonResponse({'status': 'success', 'message': 'Teacher added successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def add_driver_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            return JsonResponse({'status': 'error', 'message': 'No CSV file provided'})

        # Read CSV content
        csv_text = csv_file.read().decode('utf-8')
        lines = csv_text.split('\n')
        drivers_added = 0
        errors = []

        for i, line in enumerate(lines):
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 4:  # Name,Email,Password,Phone required
                try:
                    bus_driver = parts[0].strip()
                    email = parts[1].strip()
                    password = parts[2].strip()
                    ph_no = parts[3].strip()
                    bus_id = parts[4].strip() if len(parts) > 4 and parts[4].strip() else None
                    status = parts[5].strip() if len(parts) > 5 and parts[5].strip() else 'permanent'

                    # Check if email already exists
                    if Busdriver.objects.filter(email=email).exists():
                        errors.append(f'Row {i+1}: Email {email} already exists')
                        continue

                    bus = None
                    if bus_id:
                        try:
                            bus = Bus.objects.get(id=bus_id)
                        except Bus.DoesNotExist:
                            errors.append(f'Row {i+1}: Bus ID {bus_id} not found')
                            continue

                    driver = Busdriver(
                        bus_driver=bus_driver,
                        email=email,
                        password=password,
                        ph_no=ph_no,
                        bus_id=bus,
                        status=status
                    )
                    driver.save()
                    drivers_added += 1
                except Exception as e:
                    errors.append(f'Row {i+1}: {str(e)}')
            else:
                errors.append(f'Row {i+1}: Invalid format')

        message = f'Successfully added {drivers_added} drivers'
        if errors:
            message += f'. Errors: {len(errors)}'

        return JsonResponse({
            'status': 'success' if drivers_added > 0 else 'error',
            'message': message,
            'drivers_added': drivers_added,
            'errors': errors
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def add_management_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            return JsonResponse({'status': 'error', 'message': 'No CSV file provided'})

        # Read CSV content
        csv_text = csv_file.read().decode('utf-8')
        lines = csv_text.split('\n')
        mgmt_added = 0
        errors = []

        for i, line in enumerate(lines):
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) == 4:  # Name,Email,Password,Phone
                try:
                    name = parts[0].strip()
                    email = parts[1].strip()
                    password = parts[2].strip()
                    phone_no = parts[3].strip()

                    # Check if email already exists
                    if management.objects.filter(email=email).exists():
                        errors.append(f'Row {i+1}: Email {email} already exists')
                        continue

                    mgmt_personnel = management(
                        name=name,
                        email=email,
                        password=make_password(password),
                        phone_no=phone_no
                    )
                    mgmt_personnel.save()
                    mgmt_added += 1
                except Exception as e:
                    errors.append(f'Row {i+1}: {str(e)}')
            else:
                errors.append(f'Row {i+1}: Invalid format')

        message = f'Successfully added {mgmt_added} management personnel'
        if errors:
            message += f'. Errors: {len(errors)}'

        return JsonResponse({
            'status': 'success' if mgmt_added > 0 else 'error',
            'message': message,
            'mgmt_added': mgmt_added,
            'errors': errors
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
