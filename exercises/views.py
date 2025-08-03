# exercises/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ExerciseCategory, ExerciseGame
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import GameAttempt # Bu modeli de import ediyoruz

@login_required
def exercise_dashboard(request):
    """Tüm egzersiz kategorilerini listeleyen ana sayfa."""
    categories = ExerciseCategory.objects.filter(games__is_active=True).distinct()
    context = {
        'categories': categories
    }
    return render(request, 'exercises/exercises_dashboard.html', context)

@login_required
def play_game(request, game_slug):
    """Spesifik bir oyunu oynatacak olan sayfa."""
    game = get_object_or_404(ExerciseGame, slug=game_slug, is_active=True)
    # View'in tek görevi, modelde tanımlı olan doğru şablonu render etmek.
    # Oyunun tüm mantığı o şablonun içindeki JavaScript'te olacak.
    context = {
        'game': game
    }
    return render(request, game.template_name, context)

@login_required
@require_POST
def record_attempt_api(request):
    """
    Oyun bittiğinde JavaScript'ten gelen veriyi alır ve veritabanına kaydeder.
    """
    try:
        data = json.loads(request.body)
        game_slug = data.get('game_slug')

        if not game_slug:
            return JsonResponse({'status': 'error', 'message': 'Eksik parametre: game_slug'}, status=400)

        game = get_object_or_404(ExerciseGame, slug=game_slug)

        GameAttempt.objects.create(
            user=request.user,
            game=game,
            score=data.get('score', 0),
            correct_answers=data.get('correct', 0),
            wrong_answers=data.get('wrong', 0),
            duration_seconds=data.get('duration', 0)
        )

        return JsonResponse({'status': 'success', 'message': 'Sonuçlar başarıyla kaydedildi.'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Geçersiz JSON verisi'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)