from django.urls import path
from . import views

urlpatterns = [
    #  /ilerleme/tamamla/1/  (JS’in gönderdiği adres)
    path('tamamla/<int:ders_id>/', views.dersi_tamamla, name='ders_tamamla'),
]
    