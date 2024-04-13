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
    medicine_collection.insert_one(medicine)
    return HttpResponse(get_response(True))


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
