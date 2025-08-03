from django.urls import path
from . import views
from .views import sifre_degistir

app_name = 'kullanici'


urlpatterns = [
    path('kayit/', views.kayit_ol, name='kayit'),
    path('giris/', views.giris_yap, name='giris'),
    path('cikis/', views.cikis_yap, name='cikis'),
    path('profil/', views.profil, name='profil'),
    path('profil/duzenle/', views.profil_duzenle, name='profil_duzenle'),
    path('sifre-degistir/', sifre_degistir, name='sifre_degistir'),

]
