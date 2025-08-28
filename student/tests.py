from django.test import TestCase
from .models import student_details, student_complaints, hosteler_reg

class StudentModelTests(TestCase):
    def setUp(self):
        self.student = student_details.objects.create(
            name="John Doe",
            email="john@example.com",
            password="password123",
            phone_no="1234567890",
            stud_class="10th",
            branch="Science"
        )

    def test_student_creation(self):
        self.assertEqual(self.student.name, "John Doe")
        self.assertEqual(self.student.email, "john@example.com")

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase

class StudentViewsTests(LiveServerTestCase):
    def setUp(self):
        self.student = student_details.objects.create(
            name="John Doe",
            email="john@example.com",
            password="password123",
            phone_no="1234567890",
            stud_class="10th",
            branch="Science"
        )

    def test_login_view(self):
        response = self.client.post('/login/', {'email': 'john@example.com', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "student_dashboard.html")

    def test_logout_view(self):
        self.client.login(email='john@example.com', password='password123')
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/login/')

    def test_submit_complaint_view(self):
        response = self.client.post('/submit_complaint/', {'id': self.student.id, 'bus_id': 'Bus1', 'complaint': 'Test complaint'})
        self.assertRedirects(response, '/dashboard/')
        self.assertTrue(student_complaints.objects.filter(student_id=self.student.id).exists())

    def test_dashboard_view(self):
        self.client.login(email='john@example.com', password='password123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "student_dashboard.html")
        
    def test_live_login(self):
        # Test login via live server
        response = self.client.post(self.live_server_url + '/login/', {'email': 'john@example.com', 'password': 'password123'})
        self.assertEqual(response.status_code, 200)

    def test_live_dashboard(self):
        self.client.login(email='john@example.com', password='password123')
        response = self.client.get(self.live_server_url + '/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "student_dashboard.html")
        
    def test_live_submit_complaint(self):
        self.client.login(email='john@example.com', password='password123')
        response = self.client.post(self.live_server_url + '/submit_complaint/', {'id': self.student.id, 'bus_id': 'Bus1', 'complaint': 'Test complaint'})
        self.assertRedirects(response, self.live_server_url + '/dashboard/')
        self.assertTrue(student_complaints.objects.filter(student_id=self.student.id).exists())
