from django.db import models
from django.conf import settings

# Create your models here.
class LiveLesson(models.Model):
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='instructors_lessons'
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='students_lessons'
    )
    title = models.CharField(max_length=200, verbose_name="Ders Başlığı")
    meeting_url = models.URLField(max_length=500, verbose_name="Toplantı URL'i (Zoom Linki)")
    start_time = models.DateTimeField(verbose_name="Ders Başlangıç Zamanı")
    is_completed = models.BooleanField(default=False, verbose_name="Ders Tamamlandı mı?")

    class Meta:
        verbose_name = "Canlı Ders"
        verbose_name_plural = "Canlı Dersler"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} - {self.student.username}"