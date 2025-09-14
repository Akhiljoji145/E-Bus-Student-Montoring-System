# TODO: Update Scanning Time Windows and Location Capture

## Tasks
- [x] Update handle_boarding function in student/views.py to enforce morning scanning from 5:00am to 10:00am IST and evening from 3:45pm to 8:00pm IST
- [x] Add time range validation to reject scans outside allowed windows
- [x] Update mark_student_boarded function in driver/views.py to enforce the same time windows for manual boarding
- [x] Implement location capture mechanism in QR scan page (templates/qr_scan.html) for student boarding
- [x] Implement location capture mechanism in driver dashboard (templates/driver_dashboard.html) for manual boarding
- [x] Update backend to store latitude and longitude for both student and driver boarding
- [ ] Test the updated scanning, boarding, and location capture logic
