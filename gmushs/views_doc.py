from django.http import HttpResponse
from rest_framework.decorators import api_view
from .utilities import *
import json
from .models import *


# Create your views here.
@api_view(['GET', 'POST'])
def get_doctors(request):
    doctors = doctors_collection.find({}, {"_id": 0})
    doctors_list = []
    for doc in doctors:
        doctors_list.append(doc)

    return HttpResponse(json.dumps(doctors_list))


@api_view(['GET', 'PUT', 'DELETE'])
def delete_doctors(request, doc_id):
    if request.method == 'DELETE':
        result = doctors_collection.delete_one({"doc_id": doc_id})
        if result.deleted_count == 1:
            patient_doctor_collection.delete_one({"doc_id": doc_id})
            return HttpResponse(get_response(True))
        else:
            return HttpResponse(get_response(False))
    else:
        return HttpResponse(get_response("Bad Request"))


@api_view(['POST'])
def add_doctor(request):
    doctor = request.data

    random_id = generate_random_id(11)
    doctors = get_doctor_ids()
    while random_id in doctors:
        random_id = generate_random_id(11)

    doctor["doc_id"] = random_id
    doctors_collection.insert_one(doctor)
    return HttpResponse(get_response(True))


@api_view(['PUT'])
def update_doctor(request):
    doctor_data = request.data

    # Extract doctor ID
    doctor_id = doctor_data.get("doc_id")
    del doctor_data["doc_id"]

    # Update doctor data in the database
    result = doctors_collection.update_one({"doc_id": doctor_id}, {"$set": doctor_data})

    # Check if the update was successful
    if result.modified_count == 1:
        return HttpResponse(get_response(True))
    else:
        return HttpResponse(get_response(False), status=500)
