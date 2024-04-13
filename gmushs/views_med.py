from django.http import HttpResponse
from rest_framework.decorators import api_view
from .utilities import *
import json
from .models import *


# Create your views here.
@api_view(['GET', 'POST'])
def get_medicines(request):
    medicines = medicine_collection.find({}, {"_id": 0})
    medicines_list = []
    for med in medicines:
        medicines_list.append(med)

    return HttpResponse(json.dumps(medicines_list))


@api_view(['GET', 'PUT', 'DELETE'])
def delete_medicines(request, med_id):
    if request.method == 'DELETE':
        result = medicine_collection.delete_one({"med_id": med_id})
        if result.deleted_count == 1:
            return HttpResponse(get_response(True))
            # todo: Check if we need to delete associated medicine issued temp records if medicine gets deleted
        else:
            return HttpResponse(get_response(False))
    else:
        return HttpResponse(get_response("Bad Request"))


@api_view(['POST'])
def add_medicine(request):
    medicine = request.data

    med_id = max(get_medicine_ids()) + 1

    medicine["med_id"] = med_id
    result = medicine_collection.insert_one(medicine)
    return send_response(result.acknowledged)


@api_view(['PUT'])
def update_medicine(request):
    medicine_data = request.data

    # Extract doctor ID
    med_id = medicine_data.get("med_id")
    del medicine_data["med_id"]

    # Update doctor data in the database
    result = medicine_collection.update_one({"med_id": med_id}, {"$set": medicine_data})

    # Check if the update was successful
    if result.modified_count == 1:
        return HttpResponse(get_response(True))
    else:
        return HttpResponse(get_response(False), status=500)


@api_view(['POST', 'PUT'])
def issue_medicine(request):
    medicine_data = request.data
    quantity = medicine_collection.find_one({"med_id": medicine_data['med_id']})
    if not medicine_data['quantity'] <= quantity["quantity"]:
        return HttpResponse(get_response("No Stock: Change the quantity"))
    result = medicines_issued_temp_collection.insert_one(medicine_data)
    if result.acknowledged:
        medicine_collection.update_one({"med_id": medicine_data['med_id']},
                                       {"$set": {"quantity": quantity["quantity"] - medicine_data['quantity']}})
    return send_response(result.acknowledged)


@api_view(['GET', 'POST'])
def get_issued_medicines_temp(request, p_id):
    medicines = medicines_issued_temp_collection.find({"p_id": p_id}, {"_id": 0})
    medicines_list = []
    for m in medicines:
        medicines_list.append(m)
    return HttpResponse(json.dumps(medicines_list))


@api_view(['DELETE'])
def delete_issued_medicine(request):
    medicine_data = request.data
    if request.method == 'DELETE':
        result = medicines_issued_temp_collection.delete_one(medicine_data)
        if result.deleted_count == 1:
            quantity = medicine_collection.find_one({"med_id": medicine_data['med_id']})
            medicine_collection.update_one({"med_id": medicine_data['med_id']},
                                           {"$set": {"quantity": quantity["quantity"] + medicine_data['quantity']}})
        return send_response(result.deleted_count == 1)
    else:
        return HttpResponse(get_response("Bad Request"))
