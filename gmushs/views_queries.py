from django.http import HttpResponse
from rest_framework.decorators import api_view
from .utilities import *
import json
from .models import *
import pandas as pd


@api_view(['GET'])
def get_beds_statistics(request):
    patient_details = patient_collection.find({}, {"_id": 0})
    p_list = []
    for p in patient_details:
        p_list.append({"p_id": p["p_id"], "bedtype": p["bedtype"], "status": p["status"]})

    df = pd.DataFrame(p_list)
    res = df['bedtype'].value_counts().to_dict()
    return HttpResponse(json.dumps(res))


@api_view(['GET'])
def get_status_statistics(request):
    patient_details = patient_collection.find({}, {"_id": 0})
    p_list = []
    for p in patient_details:
        p_list.append({"p_id": p["p_id"], "bedtype": p["bedtype"], "status": p["status"]})

    df = pd.DataFrame(p_list)
    res = df['status'].value_counts().to_dict()
    return HttpResponse(json.dumps(res))


@api_view(['GET'])
def get_medicine_statistics(request):
    medicine_info = medicines_issued_collection.find({}, {"_id": 0})
    m_list = []
    for m in medicine_info:
        m_list.append({"med_id": m["med_id"], "quantity": m["quantity"]})

    df = pd.DataFrame(m_list)
    res = df.groupby('med_id')['quantity'].sum().to_dict()
    return HttpResponse(json.dumps(res))
