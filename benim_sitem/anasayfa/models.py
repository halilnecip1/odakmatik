# anasayfa/models.py
from django.db import models
from django.utils.text import slugify # Slug oluşturmak için

class Makale(models.Model):
    baslik = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200, blank=True, help_text="Makale URL'si için benzersiz kısa isim")
    ozet = models.TextField(help_text="Makale listeleme sayfasında görünecek kısa özet")
    icerik = models.TextField(help_text="Makalenin tam içeriği (HTML/Markdown olabilir)")
    yayinlanma_tarihi = models.DateTimeField(auto_now_add=True)
    gorsel = models.ImageField(upload_to='makale_gorselleri/', blank=True, null=True, help_text="Makalenin görseli/kapak resmi")

    class Meta:
        ordering = ['-yayinlanma_tarihi'] # En yeni makale en üstte olsun

    def __str__(self):
        return self.baslik

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.baslik)
        super().save(*args, **kwargs)

