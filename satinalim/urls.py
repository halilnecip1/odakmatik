# satinalim/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('egitim/<int:egitim_id>/satinal/', views.satin_al, name='satin_al'),
]