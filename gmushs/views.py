from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import *
from .utilities import *


# Create your views here.
@api_view(['GET', 'POST'])
def test(request):
    return HttpResponse(get_response("App is working"))


@api_view(['POST'])
def add_patient(request):
    patient = request.data

    doctor_id = patient["doc_id"]
    del patient["doc_id"]

    random_id = generate_random_id(11)
    patients = get_patient_ids()
    while random_id in patients:
        random_id = generate_random_id(11)

    if doctor_id == 'None':
        patient["doctor_assigned"] = False
    else:
        patient["doctor_assigned"] = True
        patient_doctor_collection.insert_one({"p_id": random_id, "doc_id": doctor_id})

    patient["p_id"] = random_id
    patient["status"] = "active"
    patient_collection.insert_one(patient)
    return HttpResponse(get_response(True))


@api_view(['PUT'])
def update_patient(request):
    patient_data = request.data

    # Extract patient ID
    patient_id = patient_data.get("p_id")
    # if not patient_id:
    #     return HttpResponse("Patient ID is required for updating.", status=400)

    # Remove patient ID from the data
    # del patient_data["p_id"]

    # Update doctor assigned status if needed
    doctor_id = patient_data.get("doc_id")
    del patient_data["doc_id"]
    if doctor_id == 'None':
        patient_data["doctor_assigned"] = False
        patient_doctor_collection.delete_one({"p_id": patient_id})
    else:
        patient_data["doctor_assigned"] = True
        patient_doctor_collection.update_one({"p_id": patient_id}, {"$set": {"doc_id": doctor_id}})

    # Update patient data in the database
    result = patient_collection.update_one({"p_id": patient_id}, {"$set": patient_data})

    # Check if the update was successful
    if result.modified_count == 1:
        return HttpResponse(get_response("Patient updated successfully."))
    else:
        return HttpResponse(get_response("Failed to update patient."), status=500)


@api_view(['GET', 'POST'])
def get_patients(request):
    patients = patient_collection.find({}, {"_id": 0})
    patients_list = []
    for p in patients:
        doctor_map = patient_doctor_collection.find_one({"p_id": p["p_id"]}, {"_id": 0})
        if doctor_map:
            p["doc_id"] = doctor_map["doc_id"]
        else:
            p["doc_id"] = "None"
        patients_list.append(p)

    return HttpResponse(json.dumps(patients_list))


@api_view(['GET', 'PUT', 'DELETE'])
def delete_patients(request, p_id):
    if request.method == 'DELETE':
        result = patient_collection.delete_one({"p_id": p_id})
        if result.deleted_count == 1:
            patient_doctor_collection.delete_one({"p_id": p_id})
            return HttpResponse(get_response(True))
        else:
            return HttpResponse(get_response(False))
    else:
        return HttpResponse(get_response("Bad Request"))


@api_view(['GET', 'POST'])
def get_rooms(request):
    rooms = room_type_collection.find({}, {"_id": 0})
    rooms_list = []
    for r in rooms:
        rooms_list.append(r)

    return HttpResponse(json.dumps(rooms_list))
