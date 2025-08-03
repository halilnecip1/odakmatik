# ilerleme/models.py
from django.db import models
from django.contrib.auth.models import User
from egitimler.models import Ders

class DersTamamlama(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    ders = models.ForeignKey(Ders, on_delete=models.CASCADE)
    tamamlandi = models.BooleanField(default=False)
    tarih = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('kullanici', 'ders')

    def __str__(self):
        return f"{self.kullanici.username} - {self.ders.baslik} - {'Tamamlandı' if self.tamamlandi else 'Tamamlanmadı'}"
