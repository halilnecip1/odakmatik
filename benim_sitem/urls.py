from django.contrib import admin
from django.urls import path, include
from anasayfa import views
from django.conf import settings
from django.conf.urls.static import static
from satinalim.views import stripe_webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('kullanici/', include('kullanici.urls')),
    path('egitimler/', include('egitimler.urls')),
    path('satinalim/', include('satinalim.urls')),
    path("webhook/stripe/", stripe_webhook, name="stripe_webhook"),
    path('ilerleme/', include('ilerleme.urls')),
    path('shop/', include('shop.urls')),
    path('panel/', include('instructor.urls')), # <-- Bu satırı ekleyin
    path('student/', include('student.urls')),
    path('iletisim/', views.iletisim, name='iletisim'),       # Yeni
    path('makaleler/', views.articles, name='articles'),
    path('makaleler/<slug:slug>/', views.makale_detay, name='makale_detay'),
    path('hakkimizda/', views.about, name='about'), # YENİ SATIR
    path('referanslar/', views.references, name='references'),
    path('kvkk/', views.kvkk, name='kvkk'), # YENİ SATIR
    path('kullanim-uyelik-sozlesmesi/', views.terms_of_service, name='terms_of_service'),
    path('newsletter/', include('newsletter.urls')),
    path('egzersizler/', include('exercises.urls')),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

