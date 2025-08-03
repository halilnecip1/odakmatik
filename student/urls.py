# student/urls.py
from django.urls import path
from . import views
from exercises import views as exercises_views

app_name = "student" # Uygulama adını belirtiyoruz

urlpatterns = [
    path("dashboard/", views.student_dashboard, name="dashboard"),
    path("egitimlerim/", views.student_trainings, name="student_trainings"),
    path("egitimlerim/<int:assigned_course_id>/complete-day/<int:day_number>/", views.complete_day, name='complete_day'), # YENİ
    path('egzersizler/', exercises_views.exercise_dashboard, name='student_exercises'),
    path("profilim/", views.student_profile_view, name="profile_view"), # Profil görüntüleme
    path("profilim/guncelle/", views.student_profile_update, name="profile_update"), # Profil güncelleme
    path("logout/", views.student_logout_view, name="logout"), # Çıkış
    path('atanan-urunlerim/', views.my_assigned_products, name='my_assigned_products'),
    path('canli-ders/', views.live_lesson_view, name='live_lesson'),
]