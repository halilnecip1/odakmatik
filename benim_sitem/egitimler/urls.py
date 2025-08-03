from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt
from egitimler.views import stripe_webhook

app_name = 'egitimler' # <-- Bu satırı ekledik!


urlpatterns = [
    path('', views.egitim_listesi, name='egitim_listesi'),
    path('<int:egitim_id>/', views.egitim_detay, name='egitim_detay'),
    path('<int:egitim_id>/satin-al/', views.satin_al, name='egitim_satin_al'),  # ← BUNU EKLE
    path('<int:egitim_id>/odeme/', views.egitim_odemesi, name='egitim_odemesi'),
    path('<int:egitim_id>/odeme-basarili/', views.odeme_basarili, name='odeme_basarili'),
    path('webhook/stripe/', csrf_exempt(stripe_webhook), name='stripe_webhook'),
    path('ders/<int:ders_id>/', views.ders_detay, name='ders_detay'),



]
