from django.http import HttpResponse
from rest_framework.decorators import api_view
from .utilities import *
import json
from .models import *
from datetime import datetime


# Create your views here.
@api_view(['GET'])
# def calculate_bill(request, p_id):
#     patient_data = patient_collection.find_one({"p_id": p_id}, {"_id": 0})
#     room_price = room_type_collection.find_one({"type": patient_data["bedtype"]}, {"_id": 0})
#     room_price = room_price["price"]
#
#     diagnostics_data = diagnostics_ordered_temp_collection.find({"p_id": p_id}, {"_id": 0})
#     medicines_data = medicines_issued_temp_collection.find({"p_id": p_id}, {"_id": 0})
#
#     diagnostics_price = 0
#     for d in diagnostics_data:
#         price = diagnostics_collection.find_one({"d_id": d["d_id"]}, {"_id": 0, "d_cost": 1})["d_cost"]
#         diagnostics_price += price
#
#     medicines_price = 0
#     for m in medicines_data:
#         price = medicine_collection.find_one({"med_id": m["med_id"]}, {"_id": 0, "price": 1})["price"]
#         medicines_price += price * m["quantity"]
#
#     no_of_days = datetime.strptime(datetime.now().strftime('%Y-%m-%d'),
#                                    "%Y-%m-%d") - datetime.strptime(patient_data["doj"],
#                                                                    "%Y-%m-%d")
#     room_price = room_price * no_of_days.days
#
#     result = {
#         "bill_id": generate_random_id(26),
#         "p_id": patient_data["p_id"],
#         "med_price": medicines_price,
#         "d_price": diagnostics_price,
#         "room_price": room_price,
#         "total": medicines_price + diagnostics_price + room_price,
#         "status": "not purchased"
#     }
#
#     check_bill = patient_billing_collection.find_one({"p_id": patient_data["p_id"]}, {"_id": 0, "p_id": 1})
#     if check_bill:
#         del result["bill_id"]
#         res = patient_billing_collection.update_one({"p_id": patient_data["p_id"]}, {"$set": result})
#         return send_response(res.modified_count == 1)
#     else:
#         res = patient_billing_collection.insert_one(result)
#         return send_response(res.acknowledged)
def calculate_bill(request, p_id):
    patient_data = db.patient.find_one({"p_id": p_id}, {"_id": 0})

    room_price_doc = db.room_type.find_one({"type": patient_data["bedtype"]}, {"_id": 0})
    room_price = room_price_doc["price"]

    pipeline = [
        {"$match": {"p_id": p_id}},
        {"$facet": {
            "diagnostics_data": [
                {"$lookup": {
                    "from": "diagnostics_ordered_temp",
                    "localField": "p_id",
                    "foreignField": "p_id",
                    "as": "diagnostics_ordered"
                }},
                {"$unwind": {"path": "$diagnostics_ordered", "preserveNullAndEmptyArrays": True}},
                {"$lookup": {
                    "from": "diagnostics",
                    "localField": "diagnostics_ordered.d_id",
                    "foreignField": "d_id",
                    "as": "diagnostics_info"
                }},
                {"$unwind": {"path": "$diagnostics_info", "preserveNullAndEmptyArrays": True}},
                {"$group": {
                    "_id": None,
                    "total_diagnostics_price": {"$sum": "$diagnostics_info.d_cost"}
                }}
            ],
            "medicines_data": [
                {"$lookup": {
                    "from": "medicines_issued_temp",
                    "localField": "p_id",
                    "foreignField": "p_id",
                    "as": "medicines_issued"
                }},
                {"$unwind": {"path": "$medicines_issued", "preserveNullAndEmptyArrays": True}},
                {"$lookup": {
                    "from": "medicine",
                    "localField": "medicines_issued.med_id",
                    "foreignField": "med_id",
                    "as": "medicine_info"
                }},
                {"$unwind": {"path": "$medicine_info", "preserveNullAndEmptyArrays": True}},
                {"$group": {
                    "_id": None,
                    "total_medicines_price": {
                        "$sum": {"$multiply": ["$medicine_info.price", "$medicines_issued.quantity"]}}
                }}
            ]
        }}
    ]

    results = list(patient_collection.aggregate(pipeline))

    # Retrieve total diagnostics price
    diagnostics_price = results[0]["diagnostics_data"][0]["total_diagnostics_price"] if results[0][
        "diagnostics_data"] else 0

    # Retrieve total medicines price
    medicines_price = results[0]["medicines_data"][0]["total_medicines_price"] if results[0]["medicines_data"] else 0

    # Calculate number of days
    no_of_days = (datetime.now() - datetime.strptime(patient_data["doj"], "%Y-%m-%d")).days

    if no_of_days == 0:
        no_of_days = 1

    # Calculate room price
    room_price *= no_of_days

    # Calculate total bill
    total_bill = medicines_price + diagnostics_price + room_price

    # Construct bill object
    bill_data = {
        "bill_id": generate_random_id(26),
        "p_id": patient_data["p_id"],
        "med_price": medicines_price,
        "d_price": diagnostics_price,
        "room_price": room_price,
        "total": total_bill,
        "status": "not purchased"
    }

    check_bill = patient_billing_collection.find_one({"p_id": patient_data["p_id"]}, {"_id": 0, "p_id": 1})

    # Update or insert bill
    if check_bill:
        res = patient_billing_collection.update_one({"p_id": patient_data["p_id"]}, {"$set": bill_data})
        return send_response(res.modified_count == 1)
    else:
        res = patient_billing_collection.insert_one(bill_data)
        return send_response(res.acknowledged)


@api_view(['GET'])
def get_bill(request, p_id):
    result = patient_billing_collection.find_one({"p_id": p_id}, {"_id": 0})
    return HttpResponse(json.dumps(result))


@api_view(['GET', 'POST'])
def make_payment(request, p_id):
    m_temp = medicines_issued_temp_collection.find({"p_id": p_id}, {"_id": 0})
    m_list = []
    for m in m_temp:
        m_list.append(m)

    d_temp = diagnostics_ordered_temp_collection.find({"p_id": p_id}, {"_id": 0})
    d_list = []
    for d in d_temp:
        d_list.append(d)

    res = True
    if m_list:
        res = medicines_issued_collection.insert_many(m_list).acknowledged
    if d_list:
        res = res and diagnostics_ordered_collection.insert_many(d_list).acknowledged

    if res:
        medicines_issued_temp_collection.delete_many({"p_id": p_id})
        diagnostics_ordered_temp_collection.delete_many({"p_id": p_id})

    res = patient_billing_collection.update_one({"p_id": p_id}, {"$set": {"status": "purchased"}}).modified_count == 1
    res = res and patient_collection.update_one({"p_id": p_id}, {"$set": {"status": "discharged"}}).modified_count == 1

    return send_response(res)
