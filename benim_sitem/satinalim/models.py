# 1️⃣ satinalim/models.py  (yeni alan eklendi)
from django.db import models
from django.contrib.auth.models import User
from egitimler.models import Egitim

class SatinAlim(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    egitim   = models.ForeignKey(Egitim, on_delete=models.CASCADE)
    tarih    = models.DateTimeField(auto_now_add=True)

    # ilerleme yüzdesi (0‑100). otomatik güncellenecek
    ilerleme_orani = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.kullanici.username} – {self.egitim.baslik} (%{self.ilerleme_orani})"
