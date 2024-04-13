import json
import random
import string
from .models import *


def generate_random_id(length):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def get_patient_ids():
    patients = []
    for patient in patient_collection.find({}, {"_id": 0, "p_id": 1}):
        patients.append(patient["p_id"])
    return patients


def get_doctor_ids():
    doctors = []
    for doctor in doctors_collection.find({}, {"_id": 0, "doc_id": 1}):
        doctors.append(doctor["doc_id"])
    return doctors


def get_response(out):
    return json.dumps({"status": out})
