from django.urls import path

from . import views

# URL Configuration
urlpatterns = [
    path('', views.test),
    path('add/', views.add),
    path('show/', views.get_persons)
]
