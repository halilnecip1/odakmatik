# instructor/urls.py
from django.urls import path
from . import views

app_name = "instructor"

urlpatterns = [
    # Mevcut Eğitmen Paneli URL'leri
    path("dashboard/", views.dashboard, name="dashboard"),
    path("ogrencilerim/", views.ogrencilerim_listesi, name="ogrencilerim_listesi"),
    path("ogrenci-ekle/", views.ogrenci_ekle, name="ogrenci_ekle"),
    path('egitimler/', views.egitimler, name='egitimler'),
    path('egzersizler/', views.egzersizler, name='egzersizler'),
    path('testler/', views.testler, name='testler'),
    path('ogrenci/<int:ogrenci_id>/', views.ogrenci_detay, name='ogrenci_detay'),
    path("ogrenci-cikar/<int:student_id>/", views.ogrenci_cikar, name="ogrenci_cikar"),
    path("ogrenci/<int:student_id>/sinif-ata/", views.assign_student_class, name="assign_student_class"),
    path("logout/", views.logout_view, name="logout"),
    
    # Profil Yönetimi URL'leri
    path("profilim/", views.profile_view, name="profile_view"),
    path("profilim/guncelle/", views.profile_update_view, name="profile_update"),
    
    # Kurs Atama/Kaldırma URL'leri
    path("ogrenci/<int:ogrenci_id>/kurs-ata/", views.assign_course_to_student, name='assign_course_to_student'),
    path("kurs-kaldir/<int:assigned_course_id>/", views.unassign_course_from_student, name='unassign_course_from_student'),
    
    # Yeni Sipariş ve Kredi Sistemi URL'leri
    path("siparis-yonetimi/yeni-siparis/", views.instructor_new_order, name="instructor_new_order"), # Ürünleri listeleme ve sepete ekleme
    path("siparis-yonetimi/siparislerim/", views.instructor_order_history, name="instructor_order_history"), # Geçmiş siparişler
    path("siparis-yonetimi/odeme-bildirimleri/", views.instructor_payment_notifications, name="instructor_payment_notifications"), # Ödeme bildirimleri (şimdilik placeholder)
    
    path('kredilerim/', views.my_credits, name='my_credits'), # Kredileri görüntüleme ve kullanma sayfası
    path('kredi-kullan/', views.use_credit, name='use_credit'), # Kredi kullanma (öğrenciye ürün atama) POST
    
    # Sepet ve Ödeme İşlemleri
    path('sepete-ekle/<int:product_id>/', views.add_to_cart, name='add_to_cart'), # Sepete ürün ekleme
    path('sepetten-cikar/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'), # Sepetten ürün çıkarma
    path('satin-al/', views.purchase_product, name='purchase_product'), # Sepetteki ürünleri satın alma (Stripe)
    
    # Ödeme Sonucu Yönlendirme URL'leri (Stripe'dan dönecek)
    path("siparis/basarili/", views.payment_success, name="payment_success"),
    path("siparis/iptal/", views.payment_cancel, name="payment_cancel"),

    path("ogrenci/<int:student_id>/planla/", views.schedule_live_lesson, name="schedule_live_lesson"),
    path("canli-dersler/", views.list_live_lessons, name="list_live_lessons"),

    
]