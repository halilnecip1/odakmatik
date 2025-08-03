
# newsletter/admin.py
from django.contrib import admin
from .models import Subscriber

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_type', 'subscribed_at') # Admin listesinde hangi alanlar görünsün
    list_filter = ('user_type', 'subscribed_at') # User type'a göre filtreleme
    search_fields = ('email',) # E-posta adresine göre arama
    ordering = ('-subscribed_at',) # En yeni aboneler üstte