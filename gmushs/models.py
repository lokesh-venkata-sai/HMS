from django.db import models
from db_connection import db

# Create your models here.
diagnostics_collection = db['diagnostics']
diagnostics_ordered_collection = db['diagnostics_ordered']
diagnostics_ordered_temp_collection = db['diagnostics_ordered_temp']
doctors_collection = db['doctor']
medicine_collection = db['medicine']
medicines_issued_collection = db['medicines_issued']
medicines_issued_temp_collection = db['medicines_issued_temp']
patient_collection = db['patient']
patient_billing_collection = db['patient_billing']
patient_doctor_collection = db['patient_doctor']
room_type_collection = db['room_type']