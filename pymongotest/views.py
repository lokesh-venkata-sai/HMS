from django.shortcuts import render
from django.http import HttpResponse
from .models import person_collection
import json


# Create your views here.
def test(request):
    return HttpResponse("App is working")


def add(request):
    records = {
        "firstname": "john",
        "lastname": "smith"
    }

    person_collection.insert_one(records)
    return HttpResponse("Person Added")


def get_persons(request):
    persons = person_collection.find({}, {"_id": 0, "firstname": 1, "lastname": 1})
    persons_list = []
    for p in persons:
        persons_list.append(p)

    print(persons_list)
    return HttpResponse(json.dumps(persons_list))
