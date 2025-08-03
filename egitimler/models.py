from django.db import models
from django.contrib.auth.models import User

class Egitim(models.Model):
    SEVIYE_SECENEKLERI = [
        ('Baslangic', 'Başlangıç'),
        ('Orta', 'Orta'),
        ('Ileri', 'İleri')
    ]

    baslik = models.CharField(max_length=200)
    aciklama = models.TextField()
    seviye = models.CharField(max_length=20, choices=SEVIYE_SECENEKLERI, default='Baslangic')
    sure = models.PositiveIntegerField(
        help_text="Ders süresi (dakika cinsinden)", 
        default=0  # <- Burayı ekle
    )
    fiyat = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0.0  # <- Burayı da ekle
    )
    gorsel = models.ImageField(upload_to='egitim_gorselleri/', null=True, blank=True)
    video = models.FileField(upload_to='egitim_videolari/', null=True, blank=True)  # yeni alan
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.baslik
    
class Ders(models.Model):
    egitim = models.ForeignKey('Egitim', on_delete=models.CASCADE, related_name='dersler')
    baslik = models.CharField(max_length=255)
    icerik = models.TextField(blank=True)
    video_url = models.URLField(blank=True)     

    def __str__(self):
        return f"{self.egitim.baslik} - {self.baslik}"