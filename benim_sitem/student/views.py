# student/views.py
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from instructor.models import KursIlerleme, EgzersizKaydi, OdevDurumu, Profile, AssignedCourse, Course, AssignedProduct
from instructor.forms import ProfileUpdateForm # Aynı formu kullanabiliriz
from exercises.models import GameAttempt
from django.db.models import Sum, Count
from datetime import date
from .models import LiveLesson # En üste bu import'u ekleyin
from django.utils import timezone

@login_required
def student_dashboard(request):
    """
    Öğrenci paneli ana sayfası.
    Hem eski verileri hem de yeni egzersiz istatistiklerini içerir.
    """
    user = request.user

    # --- YENİ EGZERSİZ İSTATİSTİKLERİNİ HESAPLAMA ---
    today = date.today()
    
    # Günlük istatistikler (Tüm oyunların toplamı)
    daily_attempts = GameAttempt.objects.filter(user=user, timestamp__date=today)
    daily_stats = daily_attempts.aggregate(
        total_score=Sum('score'),
        correct_sum=Sum('correct_answers'),
        wrong_sum=Sum('wrong_answers')
    )
    
    # Tüm zamanlar istatistikleri (Tüm oyunların toplamı)
    all_time_attempts = GameAttempt.objects.filter(user=user)
    all_time_stats = all_time_attempts.aggregate(
        total_score=Sum('score'),
        correct_sum=Sum('correct_answers'),
        wrong_sum=Sum('wrong_answers')
    )

    # --- ESKİ VERİLERİNİZ OLDUĞU GİBİ KORUNUYOR ---
    tepki_suresi_gelisimi = "0%"
    dikkat_odaklanma_gelisimi = "0%"
    hafiza_gelisimi = "0%"
    zihinsel_matematik_gelisimi = "0%"
    tepki_suresi_en_iyi_puan = "Yok"
    dikkat_odaklanma_en_iyi_puan = "Yok"
    hafiza_en_iyi_puan = "Yok"
    zihinsel_matematik_en_iyi_puan = "Yok"
    ilk_okuma_hizi = "58 k/dk"
    ilk_anlama_orani = "%50"
    son_okuma_hizi = "-"
    son_anlama_orani = "-"

    # --- TÜM VERİLERİ BİRLEŞTİREN CONTEXT ---
    context = {
        # Yeni istatistik verisi
        'stats': {
            'daily': daily_stats,
            'all_time': all_time_stats,
            'games_played_today': daily_attempts.count(),
            'total_games_played': all_time_attempts.count(),
        },
        # Eski verileriniz
        'user': user,
        'tepki_suresi_gelisimi': tepki_suresi_gelisimi,
        'dikkat_odaklanma_gelisimi': dikkat_odaklanma_gelisimi,
        'hafiza_gelisimi': hafiza_gelisimi,
        'zihinsel_matematik_gelisimi': zihinsel_matematik_gelisimi,
        'tepki_suresi_en_iyi_puan': tepki_suresi_en_iyi_puan,
        'dikkat_odaklanma_en_iyi_puan': dikkat_odaklanma_en_iyi_puan,
        'hafiza_en_iyi_puan': hafiza_en_iyi_puan,
        'zihinsel_matematik_en_iyi_puan': zihinsel_matematik_en_iyi_puan,
        'ilk_okuma_hizi': ilk_okuma_hizi,
        'ilk_anlama_orani': ilk_anlama_orani,
        'son_okuma_hizi': son_okuma_hizi,
        'son_anlama_orani': son_anlama_orani,
    }
    return render(request, "student/student_dashboard.html", context)

@login_required
def student_trainings(request): # Bu fonksiyonun adını projenizdeki gerçek view adı ile değiştirin
    # Mevcut öğrenciye atanan tüm kursları çek
    # Sadece request.user (giriş yapmış öğrenci) için olanları listeleyeceğiz
    assigned_courses = AssignedCourse.objects.filter(student=request.user).select_related('course').order_by('-assigned_at')

    context = {
        'assigned_courses': assigned_courses,
        # Diğer bağlam verileri (sidebar bilgileri vb.)
    }
    return render(request, 'student/student_trainings.html', context) # Şablon adını kontrol edin

@login_required
def complete_day(request, assigned_course_id, day_number):
    """
    Belirli bir kursun belirli bir gününü tamamlar.
    """
    assigned_course = get_object_or_404(AssignedCourse, id=assigned_course_id, student=request.user)

    day_number = int(day_number) # URL'den gelen gün numarasını int'e çevir

    # Sadece henüz tamamlanmamış günleri tamamlamaya izin ver
    if day_number == assigned_course.completed_days + 1: # Sadece bir sonraki günü tamamlamaya izin ver
        if assigned_course.completed_days < assigned_course.course.total_days:
            assigned_course.completed_days += 1
            assigned_course.save()
            messages.success(request, f"'{assigned_course.course.title}' kursunun {day_number}. günü başarıyla tamamlandı!")
        else:
            messages.info(request, f"'{assigned_course.course.title}' kursunun tüm günleri zaten tamamlanmış.")
    elif day_number <= assigned_course.completed_days:
        messages.warning(request, f"'{assigned_course.course.title}' kursunun {day_number}. günü zaten tamamlanmış.")
    else:
        messages.error(request, f"'{assigned_course.course.title}' kursunun {day_number}. gününü tamamlamak için önceki günleri bitirmelisiniz.")
        
    # Kurs detay sayfasına veya eğitimler ana sayfasına geri dön
    return redirect('student:student_trainings') # Yönlendirme URL adını kontrol edin



@login_required
def student_exercises(request):
    """
    Öğrenci paneli egzersizler sayfası.
    4. resimdeki tasarımı karşılayacak.
    """
    # Egzersiz kategorileri, her birine ileride oyunlar eklenecek
    exercises = [
        {'name': 'Göz Çalışmaları', 'icon': 'eye'},
        {'name': 'Dikkat & Odaklanma', 'icon': 'target'},
        {'name': 'Hız', 'icon': 'speedometer'}, # speed icon for example
        {'name': 'Hafıza', 'icon': 'brain'}, # brain icon for example
        {'name': 'Zihinsel Matematik', 'icon': 'calculator'}, # calculator icon for example
        {'name': 'Diğer Egzersizler', 'icon': 'more'}, # more or dots icon for example
    ]
    context = {
        'exercises': exercises
    }
    return render(request, "student/student_exercises.html", context)

@login_required
def student_profile_view(request):
    """Öğrencinin kendi profilini görüntülemesi."""
    user_profile = request.user.profile
    form = ProfileUpdateForm(instance=user_profile, initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name
    })
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'student/student_profile.html', context)

@login_required
def student_profile_update(request):
    """Öğrencinin kendi profilini güncellemesi."""
    if request.method == 'POST':
        user_profile = request.user.profile
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi.')
            return redirect('student:profile_view')
        else:
            messages.error(request, 'Profil güncellenirken bir hata oluştu. Lütfen formu kontrol edin.')
            return render(request, 'student/student_profile.html', {'form': form, 'user': request.user})
    else:
        return redirect('student:profile_view')

def student_logout_view(request):
    """Kullanıcıyı oturumdan çıkarır ve ana sayfaya yönlendirir."""
    logout(request)
    messages.info(request, "Başarıyla çıkış yaptınız.")
    return redirect('index') # 'index' ana sayfanızın URL adı olmalı (benim_sitem/urls.py'de)



@login_required
def my_assigned_products(request):
    """
    Öğrencinin kendisine atanan ürünleri görüntülediği sayfa.
    """
    # Giriş yapmış öğrenciye atanan ürünleri çekiyoruz
    assigned_products = AssignedProduct.objects.filter(
        student=request.user,
        is_used=True # Sadece kullanılmış (yani ataması yapılmış) ürünleri gösteriyoruz
    ).select_related('instructor', 'product').order_by('-assigned_date')

    context = {
        'assigned_products': assigned_products,
    }
    return render(request, 'student/my_assigned_products.html', context)

@login_required
def live_lesson_view(request):
    # Öğrencinin gelecekteki ve henüz tamamlanmamış derslerini al
    upcoming_lessons = LiveLesson.objects.filter(
        student=request.user, 
        start_time__gte=timezone.now(),
        is_completed=False
    ).order_by('start_time')

    context = {
        'lessons': upcoming_lessons
    }
    return render(request, 'student/live_lesson.html', context)