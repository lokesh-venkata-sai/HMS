from django.urls import path

from . import views, views_doc

# URL Configuration
urlpatterns = [
    path('', views.test),
    path('add_patient', views.add_patient),
    path('update_patient', views.update_patient),
    path('get_patient', views.get_patients),
    path('delete_patient/<str:p_id>', views.delete_patients),
    path('add_doctor', views_doc.add_doctor),
    path('update_doctor', views_doc.update_doctor),
    path('get_doctors', views_doc.get_doctors),
    path('delete_doctor/<str:doc_id>', views_doc.delete_doctors),
    path('get_room_type', views.get_rooms)
]
