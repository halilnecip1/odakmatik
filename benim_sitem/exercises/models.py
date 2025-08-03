# exercises/models.py

from django.db import models
from django.conf import settings

class ExerciseCategory(models.Model):
    """Egzersiz kategorilerini tutar (örn: Hafıza, Dikkat & Odaklanma)."""
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(unique=True, help_text="URL için benzersiz kısa isim, örn: 'dikkat-odaklanma'")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    icon_class = models.CharField(max_length=50, blank=True, help_text="FontAwesome ikon sınıfı, örn: 'fas fa-brain'", verbose_name="İkon Sınıfı")
    order = models.PositiveIntegerField(default=0, help_text="Sıralama için kullanılır, küçük olan önce gelir.")

    class Meta:
        verbose_name = "Egzersiz Kategorisi"
        verbose_name_plural = "Egzersiz Kategorileri"
        ordering = ['order']

    def __str__(self):
        return self.name

class ExerciseGame(models.Model):
    """Her bir spesifik oyunu tanımlar (örn: Eşleştirme Kartları)."""
    category = models.ForeignKey(ExerciseCategory, on_delete=models.CASCADE, related_name='games', verbose_name="Kategori")
    name = models.CharField(max_length=100, verbose_name="Oyun Adı")
    slug = models.SlugField(unique=True, help_text="URL için benzersiz kısa isim, örn: 'eslestirme-kartlari'")
    description = models.TextField(blank=True, verbose_name="Oyun Açıklaması")
    template_name = models.CharField(max_length=200, help_text="Bu oyunun oynanacağı HTML şablonunun yolu, örn: 'exercises/games/memory_pairs.html'")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        verbose_name = "Egzersiz Oyunu"
        verbose_name_plural = "Egzersiz Oyunları"
        ordering = ['name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class GameAttempt(models.Model):
    """Bir öğrencinin bir oyunu her oynayışının sonucunu kaydeder."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_attempts', verbose_name="Kullanıcı")
    game = models.ForeignKey(ExerciseGame, on_delete=models.CASCADE, related_name='attempts', verbose_name="Oyun")
    score = models.IntegerField(default=0, verbose_name="Puan")
    correct_answers = models.PositiveIntegerField(default=0, verbose_name="Doğru Sayısı")
    wrong_answers = models.PositiveIntegerField(default=0, verbose_name="Yanlış Sayısı")
    duration_seconds = models.PositiveIntegerField(default=0, help_text="Oyunun tamamlanma süresi (saniye)", verbose_name="Süre (saniye)")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Oynanma Zamanı")

    class Meta:
        verbose_name = "Oyun Denemesi"
        verbose_name_plural = "Oyun Denemeleri"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.game.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"