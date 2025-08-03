# shop/models.py
from django.db import models
from django.conf import settings

# Mevcut Product ve Purchase modelleriniz
class Product(models.Model):
    ROLE_CHOICES = [
        ('instructor', 'Eğitmen Yazılımı'),
        ('student', 'Öğrenci Yazılımı'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price_cents = models.IntegerField(help_text="Fiyat (kuruş cinsinden)")

    def __str__(self):
        return self.get_role_display()

class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_manually = models.BooleanField(default=False)

    def __str__(self):
        status = "Ödendi" if self.paid else "Ödenmedi"
        manual = "Manuel" if self.assigned_manually else "Otomatik"
        return f"{self.user} - {self.product} - {status} - {manual}"


# Yeni Eklenecek Modeller

class Kitap(models.Model):
    # 4 spaces indentation for the fields inside the class
    slug = models.CharField(max_length=100, unique=True, help_text="Kitap için benzersiz kısa isim (URL'de kullanılacak)")
    baslik = models.CharField(max_length=200)
    yazar = models.CharField(max_length=100)
    aciklama = models.TextField()
    fiyat_kurus = models.IntegerField(help_text="Fiyat (kuruş cinsinden)")
    icerik_url = models.URLField(blank=True, null=True, help_text="Kitabın dijital içeriğinin URL'si (PDF, e-kitap vb.)")
    resim = models.ImageField(upload_to='kitap_resimleri/', blank=True, null=True, help_text="Kitabın kapak resmi") # Make sure this is also correctly indented

    def __str__(self): # This method should also be indented correctly
        return self.baslik

class KitapSatınAlım(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    kitap = models.ForeignKey(Kitap, on_delete=models.CASCADE)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    odendi = models.BooleanField(default=False)
    satinalma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Bir kullanıcının aynı kitabı birden fazla kez ödemeden satın almasını engeller
        unique_together = ('user', 'kitap', 'odendi',) # 'odendi' alanı ile beraber benzersizlik kontrolü

    def __str__(self):
        status = "Ödendi" if self.odendi else "Ödenmedi"
        return f"{self.user} - {self.kitap.baslik} - {status}"


class Oyun(models.Model):
    slug = models.CharField(max_length=100, unique=True, help_text="Oyun için benzersiz kısa isim (URL'de kullanılacak)")
    baslik = models.CharField(max_length=200)
    platform = models.CharField(max_length=100) # Örneğin "PC", "Mobil", "Konsol"
    yapimci = models.CharField(max_length=100)
    aciklama = models.TextField()
    fiyat_kurus = models.IntegerField(help_text="Fiyat (kuruş cinsinden)")
    icerik_url = models.URLField(blank=True, null=True, help_text="Oyunun indirme veya erişim linki")

    # YENİ EKLENECEK SATIR
    resim = models.ImageField(upload_to='oyun_resimleri/', blank=True, null=True, help_text="Oyunun görseli/kapak resmi")

    def __str__(self):
        return self.baslik

class OyunSatınAlım(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    oyun = models.ForeignKey(Oyun, on_delete=models.CASCADE)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    odendi = models.BooleanField(default=False)
    satinalma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'oyun', 'odendi',)

    def __str__(self):
        status = "Ödendi" if self.odendi else "Ödenmedi"
        return f"{self.user} - {self.oyun.baslik} - {status}"
    
