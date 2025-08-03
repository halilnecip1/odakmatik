# instructor/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model() # settings.AUTH_USER_MODEL yerine daha esnek kullanım

# Existing Models (Mevcut Modelleriniz - varsayılan User modelini kullanıyorsanız)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default_profile_pic.png', blank=True, null=True)
    is_instructor = models.BooleanField(default=False, verbose_name="Eğitmen Mi?")

    def __str__(self):
        return f'{self.user.username} Profile'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'): # Profil zaten varsa kaydet
        instance.profile.save()
    # else: # Profil yoksa oluştur (eğer create_user_profile sinyali çalışmazsa)
    #    Profile.objects.create(user=instance)


class Course(models.Model):
    title = models.CharField(max_length=200)
    total_days = models.IntegerField(default=0)
    exercises_per_day = models.IntegerField(default=14)

    def __str__(self):
        return self.title

class AssignedCourse(models.Model):
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_courses"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="my_assigned_courses"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name="Atanan Kurs")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Atanma Tarihi")
    completed_days = models.IntegerField(default=0, verbose_name="Bitirilen Gün Sayısı")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Son Güncelleme Tarihi")

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

    @property
    def progress_percentage(self):
        if self.course and self.course.total_days > 0:
            return int((self.completed_days / self.course.total_days) * 100)
        return 0

    @property
    def is_completed(self):
        return self.completed_days >= self.course.total_days
    
    @property
    def next_day_to_complete(self):
        if self.is_completed or self.course.total_days == 0:
            return None
        return self.completed_days + 1

class InstructorStudent(models.Model):
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="my_students"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_instructor"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    student_class = models.IntegerField(null=True, blank=True, verbose_name="Öğrenci Sınıfı")
    
    duration_months = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="Abonelik Süresi (Ay)",
        help_text="Öğrencinin eğitmenle olan abonelik süresi (ay cinsinden)."
    )
    end_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Abonelik Bitiş Tarihi",
        help_text="Öğrencinin aboneliğinin biteceği tarih."
    )

    class Meta:
        unique_together = ("instructor", "student")

    def __str__(self):
        return f"{self.instructor.username} -> {self.student.username}"

    def save(self, *args, **kwargs):
        calculated_duration = None
        if self.duration_months is not None:
            try:
                calculated_duration = int(self.duration_months)
            except (ValueError, TypeError):
                calculated_duration = None 

        if calculated_duration is not None:
            should_update_end_date = False
            if not self.pk:
                should_update_end_date = True
            else:
                try:
                    original = InstructorStudent.objects.get(pk=self.pk)
                    if original.duration_months != calculated_duration or original.end_date is None:
                        should_update_end_date = True
                except InstructorStudent.DoesNotExist:
                    should_update_end_date = True
            
            if should_update_end_date:
                self.end_date = date.today() + relativedelta(months=+calculated_duration)
        else:
            self.end_date = None

        super().save(*args, **kwargs)

    @property
    def remaining_time(self):
        if self.end_date:
            today = date.today()
            time_left = self.end_date - today
            remaining_days = time_left.days
            
            if remaining_days < 0:
                return "Süresi Doldu"
            elif remaining_days == 0:
                return "Bugün Süresi Doluyor"
            else:
                delta = relativedelta(self.end_date, today)
                remaining_months = delta.years * 12 + delta.months
                remaining_days_after_months = delta.days

                parts = []
                if remaining_months > 0:
                    parts.append(f"{remaining_months} ay")
                if remaining_days_after_months > 0:
                    parts.append(f"{remaining_days_after_months} gün")
                
                if not parts:
                    return "Bugün Süresi Doluyor"
                
                return " ".join(parts) + " kaldı"
        return "Süre Belirtilmedi"


class KursIlerleme(models.Model):
    ogrenci = models.ForeignKey(User, on_delete=models.CASCADE)
    ad = models.CharField(max_length=255)
    ilerleme = models.IntegerField(default=0) 
    durum = models.CharField(max_length=50, choices=[('devam ediyor', 'Devam Ediyor'), ('tamamlandı', 'Tamamlandı')])


class EgzersizKaydi(models.Model):
    ogrenci = models.ForeignKey(User, on_delete=models.CASCADE)
    ad = models.CharField(max_length=255)
    tarih = models.DateTimeField(auto_now_add=True)
    basari = models.CharField(max_length=100)

class OdevDurumu(models.Model):
    ogrenci = models.ForeignKey(User, on_delete=models.CASCADE)
    baslik = models.CharField(max_length=255)
    teslim_durumu = models.CharField(max_length=100, choices=[('teslim edildi', 'Teslim Edildi'), ('bekleniyor', 'Bekleniyor')])
    not_degeri = models.CharField(max_length=20, null=True, blank=True)


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Ürün Adı")
    description = models.TextField(verbose_name="Açıklama", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Ürün Resmi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_detail = models.TextField(verbose_name="Ürün İçerik Detayı", blank=True, null=True, 
                                     help_text="Bu ürünle ilgili detaylı içerik veya metin.")
    content_file = models.FileField(upload_to='product_content_files/', blank=True, null=True, 
                                     verbose_name="Ürün İçerik Dosyası (PDF, vb.)",
                                     help_text="Bu ürünle ilişkilendirilecek PDF veya diğer dosya.")
    content_link = models.URLField(max_length=500, blank=True, null=True, 
                                    verbose_name="Ürün İçerik Linki",
                                    help_text="Bu ürünle ilişkilendirilecek harici bir link (video, web sayfası, vb.).")

    subscription_months = models.IntegerField(default=0, verbose_name="Abonelik Süresi (Ay)",
                                              help_text="Bu ürün satın alındığında öğrencinin aboneliğine eklenecek ay sayısı.")

    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                         verbose_name="Orijinal Fiyat",
                                         help_text="Bu ürünün indirimsiz veya eski fiyatı. Boş bırakılırsa gösterilmez.")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"

class Order(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name="Eğitmen")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="Sipariş Tarihi")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Miktar")
    quantity = models.IntegerField(default=1, verbose_name="Adet") 
    is_paid = models.BooleanField(default=False, verbose_name="Ödendi Mi?")
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    is_used_for_assignment = models.BooleanField(default=False, verbose_name="Atama İçin Kullanıldı Mı?") 

    def __str__(self):
        return f"{self.instructor.username} - {self.product.name} - {self.order_date}"

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"
        ordering = ['-order_date']

class Credit(models.Model):
    instructor = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit_account', verbose_name="Eğitmen")
    amount = models.IntegerField(default=0, verbose_name="Kredi Miktarı") 

    def __str__(self):
        return f"{self.instructor.username} - Kredi: {self.amount}"

    class Meta:
        verbose_name = "Kredi"
        verbose_name_plural = "Krediler"

class AssignedProduct(models.Model):
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_products_by_instructor', verbose_name="Atayan Eğitmen")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_products_to_student', verbose_name="Atanan Öğrenci")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Atanan Ürün")
    assigned_date = models.DateTimeField(auto_now_add=True, verbose_name="Atama Tarihi")
    is_used = models.BooleanField(default=False, verbose_name="Kullanıldı Mı?") 

    def __str__(self):
        student_username = self.student.username if self.student.username else "Bilinmeyen Öğrenci"
        return f"{self.instructor.username} -> {student_username} - {self.product.name}"

    class Meta:
        verbose_name = "Atanan Ürün"
        verbose_name_plural = "Atanan Ürünler"
        ordering = ['-assigned_date']


# YENİ MODELLER (OKUMA VE CANLI DERS İLE İLGİLİ)
class LiveLesson(models.Model):
    title = models.CharField(max_length=255, verbose_name="Ders Başlığı")
    meeting_url = models.URLField(max_length=500, verbose_name="Toplantı Linki", help_text="Zoom, Meet vb. toplantı linki")
    start_time = models.DateTimeField(verbose_name="Ders Tarihi ve Saati")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='live_lessons_as_student', verbose_name="Öğrenci")
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='live_lessons_as_instructor', verbose_name="Eğitmen")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False, verbose_name="Tamamlandı Mı?") # Eğer böyle bir alanınız olsaydı

    class Meta:
        verbose_name = "Canlı Ders"
        verbose_name_plural = "Canlı Dersler"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} - {self.student.username} ({self.start_time.strftime('%d %b %H:%M')})"

