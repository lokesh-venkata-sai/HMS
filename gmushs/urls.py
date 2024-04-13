from django.urls import path

from . import views, views_doc, views_med, views_diag

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

    path('add_medicine', views_med.add_medicine),
    path('update_medicine', views_med.update_medicine),
    path('get_medicines', views_med.get_medicines),
    path('delete_medicine/<int:med_id>', views_med.delete_medicines),

    path('add_diagnostic', views_diag.add_diagnostic),
    path('update_diagnostic', views_diag.update_diagnostic),
    path('get_diagnostics', views_diag.get_diagnostics),
    path('delete_diagnostic/<int:d_id>', views_diag.delete_diagnostics),

    path('get_room_type', views.get_rooms)
]
