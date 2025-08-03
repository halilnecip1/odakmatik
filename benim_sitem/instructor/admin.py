# instructor/admin.py
from django.contrib import admin
from .models import InstructorStudent, Profile, Course, AssignedCourse, KursIlerleme, EgzersizKaydi, OdevDurumu
from .models import Product, Order, Credit, AssignedProduct, InstructorStudent, Course, AssignedCourse, KursIlerleme, EgzersizKaydi, OdevDurumu, Profile



@admin.register(InstructorStudent)
class InstructorStudentAdmin(admin.ModelAdmin):
    list_display = ("instructor", "student", "added_at")
    search_fields = ("instructor__username", "student__username")

admin.site.register(KursIlerleme)
admin.site.register(EgzersizKaydi)
admin.site.register(OdevDurumu)
admin.site.register(Course)
admin.site.register(AssignedCourse)
admin.site.register(Profile)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'original_price', 'subscription_months', 'is_active', 'created_at') # list_display'e eklendi
    list_filter = ('is_active', 'subscription_months')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price', 'image', 'is_active')
        }),
        ('Ürün İçeriği Bilgileri', {
            'fields': ('content_detail', 'content_file', 'content_link'),
            'description': 'Bu ürünle ilişkilendirilecek detaylı içerik ve dosyalar.'
        }),
        ('Abonelik Bilgileri', {
            'fields': ('subscription_months',),
            'description': 'Bu ürün satın alındığında öğrencinin aboneliğine eklenecek süre.'
        }),
        ('Fiyatlandırma Bilgileri', { # Yeni fieldset
            'fields': ('original_price',),
            'description': 'Ürünün indirimsiz veya eski fiyatı.'
        }),
    )
    
admin.site.register(Order)
admin.site.register(Credit)
admin.site.register(AssignedProduct)

