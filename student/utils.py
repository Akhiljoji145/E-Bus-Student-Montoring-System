from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import student_details
from django.core.mail import send_mail

token_generator = PasswordResetTokenGenerator()

def send_password_reset_email(user):
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = f"http://127.0.0.1:8000/reset-password/{uid}/{token}/"

    subject = "Password Reset Request"
    message = f"Hi {user.name},\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, ignore this email."
    
    send_mail(subject, message, 'noreply@schoolbus.com', [user.email])
