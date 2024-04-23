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
            patients = patient_doctor_collection.find({'doc_id': doc_id}, {"_id": 0, "p_id": 1})

            p_list = []
            for p in patients:
                p_list.append(p["p_id"])

            patient_doctor_collection.delete_many({"doc_id": doc_id})

            for p in p_list:
                patient_collection.update_one({"p_id": p}, {"$set": {"doctor_assigned": False}})

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


@api_view(['GET'])
# def get_doctor_by_patient(request, p_id):
#     patient = patient_collection.find_one({"p_id": p_id}, {"_id": 0})
#     doctor_map = patient_doctor_collection.find_one({"p_id": p_id}, {"_id": 0})
#
#     if doctor_map:
#         patient["doc_id"] = doctor_map["doc_id"]
#     else:
#         patient["doc_id"] = "None"
#
#     doctor = doctors_collection.find_one({"doc_id": patient["doc_id"]}, {"_id": 0})
#     res = {"patient_info": patient, "doctor_info": doctor}
#     return HttpResponse(json.dumps(res))
def get_doctor_by_patient(request, p_id):
    pipeline = [
        {
            "$match": {
                "p_id": p_id
            }
        },
        {
            "$lookup": {
                "from": "patient_doctor",
                "localField": "p_id",
                "foreignField": "p_id",
                "as": "patient_doctor_info"
            }
        },
        {
            "$unwind": "$patient_doctor_info"
        },
        {
            "$lookup": {
                "from": "doctor",
                "localField": "patient_doctor_info.doc_id",
                "foreignField": "doc_id",
                "as": "doctor_info"
            }
        },
        {
            "$unwind": "$doctor_info"
        },
        {
            "$project": {
                "_id": 0,
                "doctor_details": {
                    "doc_name": "$doctor_info.doc_name",
                    "specialization": "$doctor_info.specialization",
                    "email": "$doctor_info.email",
                    "mobile": "$doctor_info.mobile",
                    "address": "$doctor_info.address",
                    "city": "$doctor_info.city",
                    "state": "$doctor_info.state"
                },
                "patient_details": {
                    "p_id": "$p_id",
                    "p_name": "$p_name",
                    "p_age": "$p_age",
                    "p_mobile": "$p_mobile",
                    "p_email": "$p_email",
                    "address": "$address",
                    "doj": "$doj",
                    "bedtype": "$bedtype",
                    "city": "$city",
                    "state": "$state",
                    "doctor_assigned": "$doctor_assigned",
                    "status": "$status"
                },
            }
        }
    ]
    res = patient_collection.aggregate(pipeline)
    d_list = []
    patient = {}
    for doctor in res:
        d_list.append(doctor["doctor_details"])
        patient = doctor["patient_details"]
    return HttpResponse(json.dumps({"patient_info": patient, "doctor_info": d_list[0]}))
