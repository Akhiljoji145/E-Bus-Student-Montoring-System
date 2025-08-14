# from django.shortcuts import render,redirect
# from django.contrib import messages
# from .models import student_details,student_complaints
# from driver.models import Bus

# # Create your views here
# def home(request):
#     return render(request,'index.html')
# def logindashboard(request):
#     return render(request,'dashboard_login.html')
# def login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         try:
#             student = student_details.objects.get(email=email, password=password)
#             bus= Bus.objects.all()
#             complaints=student_complaints.objects.all()
#             request.session['student_id'] = student.id
#             request.session['student_name'] = student.name
#             request.session['student_email'] = student.email
#             request.session['student_class'] = student.stud_class
#             request.session['student_branch'] = student.branch
#             request.session['accommodation_type'] = student.accommodation_type
            
            
#             return render(request,'student_dashboard.html',{'student':student,'bus':bus,'complaints':complaints})
#         except student_details.DoesNotExist:
#             messages.error(request, 'Invalid email or password')
#             return render(request, 'student_login.html')
    
#     return render(request,'student_login.html')

# def logout(request):
#     # Clear session
#     if 'student_id' in request.session:
#         del request.session['student_id']
#     if 'student_name' in request.session:
#         del request.session['student_name']
#     if 'student_email' in request.session:
#         del request.session['student_email']
#     if 'student_class' in request.session:
#         del request.session['student_class']
#     if 'student_branch' in request.session:
#         del request.session['student_branch']
#     if 'accommodation_type' in request.session:
#         del request.session['accommodation_type']
    
#     return redirect('/login')

    

# def submit_complaint(request):
#     if request.method == "POST":
#         student_id=request.POST.get('id')
#         bus=request.POST.get('bus_id')
#         comp=request.POST.get('complaint')
#         complaints=student_complaints(student_id=student_id,bus=bus,complaint=comp)
#         complaints.save()
#         return redirect('/dashboard')

# def dashboard(request):
#     if 'student_id' in request.session:
#         student_id=request.session['student_id']
#         student=student_details.objects.get(id=student_id)
#         bus= Bus.objects.all()
#         complaints=student_complaints.objects.get(student=student_id)
#         return render(request,'student_dashboard.html',{'student':student,'bus':bus,'complaints':complaints})
#     else:
#         return redirect('/login')


        
    
