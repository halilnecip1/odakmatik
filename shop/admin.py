from django.contrib import admin
from .models import Product, Purchase, Kitap, KitapSatınAlım, Oyun, OyunSatınAlım

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'role', 'price_cents')

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'paid', 'assigned_manually', 'created_at')
    list_filter = ('paid', 'assigned_manually', 'product__role')
    search_fields = ('user__username', 'product__title')
    actions = ['mark_as_manual']

    def mark_as_manual(self, request, queryset):
        updated = queryset.update(assigned_manually=True)
        self.message_user(request, f"{updated} kayıt manuel olarak işaretlendi.")
    mark_as_manual.short_description = "Seçilenleri manuel atandı olarak işaretle"


# Yeni eklenecek admin kayıtları
@admin.register(Kitap)
class KitapAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'yazar', 'fiyat_kurus', 'slug')
    search_fields = ('baslik', 'yazar', 'slug')
    prepopulated_fields = {'slug': ('baslik',)} # Başlığı girerken slug otomatik oluşsun

@admin.register(KitapSatınAlım)
class KitapSatınAlımAdmin(admin.ModelAdmin):
    list_display = ('user', 'kitap', 'odendi', 'satinalma_tarihi')
    list_filter = ('odendi', 'satinalma_tarihi')
    search_fields = ('user__username', 'kitap__baslik')

@admin.register(Oyun)
class OyunAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'platform', 'yapimci', 'fiyat_kurus', 'slug')
    search_fields = ('baslik', 'platform', 'yapimci', 'slug')
    prepopulated_fields = {'slug': ('baslik',)} # Başlığı girerken slug otomatik oluşsun

@admin.register(OyunSatınAlım)
class OyunSatınAlımAdmin(admin.ModelAdmin):
    list_display = ('user', 'oyun', 'odendi', 'satinalma_tarihi')
    list_filter = ('odendi', 'satinalma_tarihi')
    search_fields = ('user__username', 'oyun__baslik')
