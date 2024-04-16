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
    if doctor_id == 'None':
        patient_data["doctor_assigned"] = False
        patient_doctor_collection.delete_one({"p_id": patient_id})
    else:
        # print("In updating doctor ID")
        if doctor_assigned:
            patient_doctor_collection.update_one({"p_id": patient_id}, {"$set": {"doc_id": doctor_id}})
        else:
            patient_data["doctor_assigned"] = True
            patient_doctor_collection.insert_one({"p_id": patient_id, "doc_id": doctor_id})

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
def get_all_patient_details(request, p_id):
    patient_data = patient_collection.find_one({"p_id": p_id}, {"_id": 0})
    diagnostics_data = diagnostics_ordered_temp_collection.find({"p_id": p_id}, {"_id": 0})
    medicines_data = medicines_issued_temp_collection.find({"p_id": p_id}, {"_id": 0})
    doc_id = patient_doctor_collection.find_one({"p_id": p_id}, {"_id": 0, 'doc_id': 1})["doc_id"]
    doctor_info = doctors_collection.find_one({"doc_id": doc_id}, {"_id": 0})

    diagnostics_list = []
    for d in diagnostics_data:
        diagnostic = diagnostics_collection.find_one({"d_id": d["d_id"]}, {"_id": 0})
        diagnostics_list.append({"d_id": d["d_id"],
                                 "d_name": diagnostic["d_name"],
                                 "date_issued": d["date_issued"]})
    medicines_list = []
    for m in medicines_data:
        medicine = medicine_collection.find_one({"med_id": m["med_id"]}, {"_id": 0})
        medicines_list.append({"med_id": m["med_id"],
                               "m_name": medicine["med_name"],
                               "quantity": m["quantity"],
                               "date_issued": m["date_issued"]})

    result = {
        "patient_info": patient_data,
        "diagnostics_info": diagnostics_list,
        "medicines_info": medicines_list,
        "doctor_info": doctor_info
    }
    return HttpResponse(json.dumps(result))


@api_view(['GET'])
def get_patients_by_doctor(request, doc_id):
    patients = patient_doctor_collection.find({'doc_id': doc_id}, {"_id": 0, "p_id": 1})
    doctor = doctors_collection.find_one({"doc_id": doc_id}, {"_id": 0})

    p_list = []
    for p in patients:
        p_list.append(patient_collection.find_one({"p_id": p["p_id"]}, {"_id": 0}))

    res = {"doctor_info": doctor, "patient_info": p_list}
    return HttpResponse(json.dumps(res))
