from django.http import HttpResponse
from rest_framework.decorators import api_view
from .utilities import *
import json
from .models import *


# Create your views here.
@api_view(['GET', 'POST'])
def get_diagnostics(request):
    diagnostics = diagnostics_collection.find({}, {"_id": 0})
    diagnostics_list = []
    for d in diagnostics:
        diagnostics_list.append(d)
    return HttpResponse(json.dumps(diagnostics_list))


@api_view(['GET', 'PUT', 'DELETE'])
def delete_diagnostics(request, d_id):
    if request.method == 'DELETE':
        result = diagnostics_collection.delete_one({"d_id": d_id})
        if result.deleted_count == 1:
            return HttpResponse(get_response(True))
            # todo: Check if we need to delete associated diagnostics issued temp records if diagnostic gets deleted
        else:
            return HttpResponse(get_response(False))
    else:
        return HttpResponse(get_response("Bad Request"))


@api_view(['POST'])
def add_diagnostic(request):
    diagnostic = request.data

    d_id = max(get_diagnostic_ids()) + 1

    diagnostic["d_id"] = d_id
    diagnostics_collection.insert_one(diagnostic)
    return HttpResponse(get_response(True))


@api_view(['PUT'])
def update_diagnostic(request):
    diagnostic_data = request.data

    # Extract doctor ID
    d_id = diagnostic_data.get("d_id")
    del diagnostic_data["d_id"]

    # Update doctor data in the database
    result = diagnostics_collection.update_one({"d_id": d_id}, {"$set": diagnostic_data})

    # Check if the update was successful
    if result.modified_count == 1:
        return HttpResponse(get_response(True))
    else:
        return HttpResponse(get_response(False), status=500)
