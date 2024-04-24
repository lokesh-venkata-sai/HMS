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

    # Update doctor assigned status if needed
    doctor_id = patient_data.get("doc_id")
    doctor_assigned = patient_collection.find_one({"p_id": patient_id},
                                                  {"_id": 0, "doctor_assigned": 1})["doctor_assigned"]
    del patient_data["doc_id"]
    doc_changed = False
    if doctor_id == 'None':
        patient_data["doctor_assigned"] = False
        patient_doctor_collection.delete_one({"p_id": patient_id})
    else:
        # print("In updating doctor ID")
        if doctor_assigned:
            doc_changed = patient_doctor_collection.update_one({"p_id": patient_id}, {"$set": {"doc_id": doctor_id}})
        else:
            patient_data["doctor_assigned"] = True
            patient_doctor_collection.insert_one({"p_id": patient_id, "doc_id": doctor_id})

    # Update patient data in the database
    result = patient_collection.update_one({"p_id": patient_id}, {"$set": patient_data})

    # Check if the update was successful
    if (result.modified_count == 1) or (doc_changed.modified_count == 1):
        return HttpResponse(get_response("Patient updated successfully."))
    else:
        return HttpResponse(get_response("Failed to update patient."))


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


@api_view(['POST'])
def add_room(request):
    rooms = request.data
    result = room_type_collection.insert_one(rooms)
    return send_response(result.acknowledged)


@api_view(['PUT'])
def update_room(request):
    room_data = request.data
    # Update doctor data in the database
    result = room_type_collection.update_one({"type": room_data["type"]}, {"$set": room_data})

    # Check if the update was successful
    return send_response(result.modified_count == 1)


@api_view(['GET', 'PUT', 'DELETE'])
def delete_room(request, room_type):
    if request.method == 'DELETE':
        result = room_type_collection.delete_one({"type": room_type})
        return send_response(result.deleted_count == 1)
    else:
        return HttpResponse(get_response("Bad Request"))


@api_view(['GET'])
# def get_all_patient_details(request, p_id):
#     patient_data = patient_collection.find_one({"p_id": p_id}, {"_id": 0})
#     if patient_data["status"] == 'active':
#         diagnostics_data = diagnostics_ordered_temp_collection.find({"p_id": p_id}, {"_id": 0})
#         medicines_data = medicines_issued_temp_collection.find({"p_id": p_id}, {"_id": 0})
#     else:
#         diagnostics_data = diagnostics_ordered_collection.find({"p_id": p_id}, {"_id": 0})
#         medicines_data = medicines_issued_collection.find({"p_id": p_id}, {"_id": 0})
#     doc_id_info = patient_doctor_collection.find_one({"p_id": p_id}, {"_id": 0, 'doc_id': 1})
#     doctor_info = {}
#     if doc_id_info:
#         doc_id = doc_id_info["doc_id"]
#         doctor_info = doctors_collection.find_one({"doc_id": doc_id}, {"_id": 0})
#
#     diagnostics_list = []
#     for d in diagnostics_data:
#         diagnostic = diagnostics_collection.find_one({"d_id": d["d_id"]}, {"_id": 0})
#         if diagnostic:
#             diagnostics_list.append({"d_id": d["d_id"],
#                                      "d_name": diagnostic["d_name"],
#                                      "date_issued": d["date_issued"]})
#     medicines_list = []
#     for m in medicines_data:
#         medicine = medicine_collection.find_one({"med_id": m["med_id"]}, {"_id": 0})
#         if medicine:
#             medicines_list.append({"med_id": m["med_id"],
#                                    "m_name": medicine["med_name"],
#                                    "quantity": m["quantity"],
#                                    "date_issued": m["date_issued"]})
#
#     result = {
#         "patient_info": patient_data,
#         "diagnostics_info": diagnostics_list,
#         "medicines_info": medicines_list,
#         "doctor_info": doctor_info
#     }
#     return HttpResponse(json.dumps(result))
def get_all_patient_details(request, p_id):
    patient_data = db.patient.find_one({"p_id": p_id}, {"_id": 0})
    diagnostics_table = "diagnostics_ordered_temp"
    medicines_table = "medicines_issued_temp"
    if patient_data["status"] == "discharged":
        diagnostics_table = "diagnostics_ordered"
        medicines_table = "medicines_issued"

    medicines_pipeline = [
        {
            "$match": {
                "p_id": p_id
            }
        },
        {
            "$lookup": {
                "from": medicines_table,
                "localField": "p_id",
                "foreignField": "p_id",
                "as": "medicines_issued1"
            }
        },
        {
            "$unwind": {
                "path": "$medicines_issued1",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$lookup": {
                "from": "medicine",
                "localField": "medicines_issued1.med_id",
                "foreignField": "med_id",
                "as": "medicine_info"
            }
        },
        {
            "$unwind": {
                "path": "$medicine_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "_id": 0,
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
                "medicine_details": {
                    "med_id": "$medicine_info.med_id",
                    "med_name": "$medicine_info.med_name",
                    "quantity": "$medicines_issued1.quantity",
                    "date_issued": "$medicines_issued1.date_issued"
                }
            }
        }
    ]
    diagnostics_pipeline = [
        {
            "$match": {
                "p_id": p_id
            }
        },
        {
            "$lookup": {
                "from": diagnostics_table,
                "localField": "p_id",
                "foreignField": "p_id",
                "as": "diagnostics_ordered"
            }
        },
        {
            "$unwind": {
                "path": "$diagnostics_ordered",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$lookup": {
                "from": "diagnostics",
                "localField": "diagnostics_ordered.d_id",
                "foreignField": "d_id",
                "as": "diagnostics_info"
            }
        },
        {
            "$unwind": {
                "path": "$diagnostics_info",
                "preserveNullAndEmptyArrays": True
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
            "$unwind": {
                "path": "$patient_doctor_info",
                "preserveNullAndEmptyArrays": True
            }
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
            "$unwind": {
                "path": "$doctor_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "_id": 0,
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
                "diagnostics_details": {
                    "d_id": "$diagnostics_info.d_id",
                    "d_name": "$diagnostics_info.d_name",
                    "date_issued": "$diagnostics_ordered.date_issued"
                },

                "doctor_details": {
                    "doc_id": "$doctor_info.doc_id",
                    "doc_name": "$doctor_info.doc_name",
                    "specialization": "$doctor_info.specialization",
                    "email": "$doctor_info.email",
                    "mobile": "$doctor_info.mobile",
                    "address": "$doctor_info.address",
                    "city": "$doctor_info.city",
                    "state": "$doctor_info.state"
                }
            }
        }
    ]

    res1 = patient_collection.aggregate(medicines_pipeline)
    res2 = patient_collection.aggregate(diagnostics_pipeline)

    temp1 = {}
    temp2 = {}
    list1 = []
    list2 = []

    for patient in res1:
        temp1 = patient["patient_details"]
        if patient["medicine_details"]:
            list1.append(patient["medicine_details"])

    for patient in res2:
        temp2 = patient["doctor_details"]
        if patient["diagnostics_details"]:
            list2.append(patient["diagnostics_details"])

    result = {}
    if temp1 or temp2:
        result = {
            "patient_info": temp1,
            "diagnostics_info": list2,
            "medicines_info": list1,
            "doctor_info": temp2
        }
    return HttpResponse(json.dumps(result))


@api_view(['GET'])
# def get_patients_by_doctor(request, doc_id):
#     patients = patient_doctor_collection.find({'doc_id': doc_id}, {"_id": 0, "p_id": 1})
#     doctor = doctors_collection.find_one({"doc_id": doc_id}, {"_id": 0})
#
#     p_list = []
#     for p in patients:
#         p_list.append(patient_collection.find_one({"p_id": p["p_id"]}, {"_id": 0}))
#
#     res = {"doctor_info": doctor, "patient_info": p_list}
#     return HttpResponse(json.dumps(res))
def get_patients_by_doctor(request, doc_id):
    doctor = doctors_collection.find_one({"doc_id": doc_id}, {"_id": 0})
    pipeline = [
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
            "$match": {
                "patient_doctor_info.doc_id": doc_id
            }
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
                }
            }
        }
    ]
    res = patient_collection.aggregate(pipeline)
    p_list = []
    for patient in res:
        p_list.append(patient["patient_details"])
    return HttpResponse(json.dumps({"doctor_info": doctor, "patient_info": p_list}))
