# exercises/admin.py

from django.contrib import admin
from .models import ExerciseCategory, ExerciseGame, GameAttempt

@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'slug') # 'name' alanını başa aldık
    list_editable = ('order',) # 'order' artık düzenlenebilir
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(ExerciseGame)
class ExerciseGameAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)

@admin.register(GameAttempt)
class GameAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'score', 'timestamp')
    list_filter = ('game', 'user', 'timestamp')
    search_fields = ('user__username', 'game__name')
    # Bu alanların admin panelinden değiştirilmesini engelliyoruz, çünkü bunlar oyun sonucu oluşur.
    readonly_fields = ('user', 'game', 'score', 'correct_answers', 'wrong_answers', 'duration_seconds', 'timestamp')

    # Admin panelinden yeni bir "GameAttempt" eklenmesini engeller.
    def has_add_permission(self, request):
        return False

    # Admin panelinden mevcut kayıtların silinmesini engeller (isteğe bağlı).
    def has_delete_permission(self, request, obj=None):
        return False