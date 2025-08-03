# anasayfa/admin.py
from django.contrib import admin
from .models import Makale # Makale modelini import ediyoruz


@admin.register(Makale)
class MakaleAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'slug', 'yayinlanma_tarihi')
    prepopulated_fields = {'slug': ('baslik',)} # Başlığı yazdıkça slug otomatik dolsun
    search_fields = ('baslik', 'icerik')
    list_filter = ('yayinlanma_tarihi',)

