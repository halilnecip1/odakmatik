from django.urls import path, include
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.public_home, name='public_home'),
    path('home/', views.home, name='home'),
    path('buy/<str:role>/', views.create_checkout, name='create_checkout'),
    path('buy/<str:product_type>/<slug:slug>/', views.create_checkout, name='create_checkout'),
    path('success/', views.success, name='success'),
    # Yeni erişim yolları
    path('kitaplar/<slug:slug>/git/', views.access_kitap, name='access_kitap'),
    path('oyunlar/<slug:slug>/git/', views.access_oyun, name='access_oyun'),

]