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


@api_view(['GET'])
def search(request):
    name = request.GET.get('query', '')
    patient_data = patient_collection.find({"p_name": {"$regex": ".*" + name + ".*", "$options": "i"}}, {"_id": 0})
    doctor_info = doctors_collection.find({"doc_name": {"$regex": ".*" + name + ".*", "$options": "i"}}, {"_id": 0})

    patients_list = []
    for p in patient_data:
        doctor_map = patient_doctor_collection.find_one({"p_id": p["p_id"]}, {"_id": 0})
        if doctor_map:
            p["doc_id"] = doctor_map["doc_id"]
        else:
            p["doc_id"] = "None"
        patients_list.append(p)

    doctors_list = []
    for d in doctor_info:
        doctors_list.append(d)

    result = {
        "patient_info": patients_list,
        "doctor_info": doctors_list
    }

    return HttpResponse(json.dumps(result))


@api_view(['GET'])
def get_timely_stat(request):
    type_time = request.GET.get('type', '')
    patient_data = patient_collection.find({}, {"_id": 0})
    patients_list = []
    for p in patient_data:
        patients_list.append(p)

    df = pd.DataFrame(patients_list)
    df['doj'] = pd.to_datetime(df['doj'])
    df['year'] = df['doj'].dt.year
    df['month'] = df['doj'].dt.month
    result = {}
    if type_time == "MONTHLY":
        year = request.GET.get('year', '')
        filtered_df = df[(df['year'] == int(year))]
        patients_count_monthly = filtered_df.groupby('month').size()
        result = patients_count_monthly.to_dict()
    elif type_time == "YEARLY":
        start_year = request.GET.get('startYear', '')
        end_year = request.GET.get('endYear', '')
        filtered_df = df[(df['year'] >= int(start_year)) & (df['year'] <= int(end_year))]
        patients_count_yearly = filtered_df.groupby('year').size()
        result = patients_count_yearly.to_dict()

    return HttpResponse(json.dumps(result))
