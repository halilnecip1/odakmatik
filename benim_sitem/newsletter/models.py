# newsletter/models.py
from django.db import models

class Subscriber(models.Model):
    # E-posta adresinin boş olmaması ve tekil olması gerekiyor
    email = models.EmailField(unique=True, verbose_name="E-posta Adresi")

    # Kullanıcı tipini seçmek için seçenekler tanımlayalım
    USER_TYPE_CHOICES = [
        ('egitmen', 'Eğitmen'),
        ('ogrenci', 'Öğrenci'),
    ]
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='ogrenci', # Varsayılan olarak öğrenci seçili olabilir
        verbose_name="Kullanıcı Tipi"
    )

    # Abone olma tarihi
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Abone Olma Tarihi")

    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})" # get_user_type_display() choices'tan okunabilir adı getirir

    class Meta:
        verbose_name = "Abone"
        verbose_name_plural = "Aboneler"
        ordering = ['-subscribed_at'] # En yeni aboneler üstte olsun