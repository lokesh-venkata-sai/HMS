from django.urls import path

from . import views, views_doc, views_med, views_diag, views_billing

# URL Configuration
urlpatterns = [
    path('', views.test),
    path('add_patient', views.add_patient),
    path('update_patient', views.update_patient),
    path('get_patient', views.get_patients),
    path('delete_patient/<str:p_id>', views.delete_patients),

    path('get_all_patient_details/<str:p_id>', views.get_all_patient_details),

    path('add_doctor', views_doc.add_doctor),
    path('update_doctor', views_doc.update_doctor),
    path('get_doctors', views_doc.get_doctors),
    path('delete_doctor/<str:doc_id>', views_doc.delete_doctors),

    path('add_medicine', views_med.add_medicine),
    path('update_medicine', views_med.update_medicine),
    path('get_medicines', views_med.get_medicines),
    path('delete_medicine/<int:med_id>', views_med.delete_medicines),

    path('issue_medicine', views_med.issue_medicine),
    path('get_issued_medicine_temp/<str:p_id>', views_med.get_issued_medicines_temp),
    path('delete_issued_medicine', views_med.delete_issued_medicine),

    path('add_diagnostic', views_diag.add_diagnostic),
    path('update_diagnostic', views_diag.update_diagnostic),
    path('get_diagnostics', views_diag.get_diagnostics),
    path('delete_diagnostic/<int:d_id>', views_diag.delete_diagnostics),

    path('issue_diagnostic', views_diag.issue_diagnostic),
    path('get_issued_diagnostic_temp/<str:p_id>', views_diag.get_issued_diagnostics_temp),
    path('delete_issued_diagnostic', views_diag.delete_issued_diagnostic),

    path('get_room_type', views.get_rooms),
    path('add_room_type', views.add_room),
    path('update_room_type', views.update_room),
    path('delete_room/<str:room_type>', views.delete_room),

    path('calculate_bill/<str:p_id>', views_billing.calculate_bill),
    path('get_bill/<str:p_id>', views_billing.get_bill),
    path('make_payment/<str:p_id>', views_billing.make_payment)
]
