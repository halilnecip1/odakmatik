# exercises/urls.py
from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    # Egzersiz ana sayfası: /egzersizler/
    path('', views.exercise_dashboard, name='exercise_dashboard'),

    # Tek bir oyunu oynatma sayfası: /egzersizler/oyna/eslestirme-kartlari/
    path('oyna/<slug:game_slug>/', views.play_game, name='play_game'),
    path('api/record-attempt/', views.record_attempt_api, name='record_attempt_api'),
]