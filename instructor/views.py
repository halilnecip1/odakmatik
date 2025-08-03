# instructor/views.py
import logging
from .forms import LiveLessonForm
from student.models import LiveLesson
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.db import transaction # Atomik işlemler için
from django.db import IntegrityError # unique_together hatası için
from django.db.models import Q, F # F objesi için (ogrenci_detay için gerekli)
from django.conf import settings # Stripe Secret Key'i için
from django.views.decorators.http import require_POST
from datetime import date # dateutil.relativedelta için gerekli
from dateutil.relativedelta import relativedelta # Abonelik süresi hesaplamaları için
from exercises.models import GameAttempt
from django.db.models import Sum, Count
from django.urls import reverse # reverse fonksiyonu için gerekli
# Kendi modellerinizi import edin
from .forms import AssignCourseForm, LiveLessonForm
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, F # Sum'u zaten kullanıyorsunuz, F'yi de ekledim
# Kendi formlarınızı import edin
from .models import (
    InstructorStudent, KursIlerleme, EgzersizKaydi, OdevDurumu,
    Profile, Course, AssignedCourse,
    Product, Order, Credit, AssignedProduct # Yeni eklenen modeller
)
from .forms import EgitmenOgrenciEkleForm, ProfileUpdateForm, AssignCourseForm

# Django'nun varsayılan User modelini alıyoruz
User = get_user_model()
logger = logging.getLogger(__name__)
# Stripe Kütüphanesini import et
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Sınıf kategorilerini tanımlıyoruz
SINIF_KATEGORILERI = {
    "ilkokul": [1, 2, 3, 4],
    "ortaokul": [5, 6, 7, 8],
    "lise": [9, 10, 11, 12],
    "tumu": list(range(1, 13)) # Tüm sınıfları kapsayan 'Tümü' seçeneği
}

# Yardımcı fonksiyon: Sınıf numarasını kategoriye çevirir (view içinde kullanılacak)
def _get_class_category(class_number):
    if class_number is None:
        return "Belirtilmemiş"
    for category, classes in SINIF_KATEGORILERI.items():
        if class_number in classes:
            if category == "ilkokul":
                return "İlkokul"
            elif category == "ortaokul":
                return "Ortaokul"
            elif category == "lise":
                return "Lise"
    return "Diğer" # 1-12 dışında bir sınıf olursa

# Eğitmen olduğunu test eden yardımcı fonksiyonu güncelledik
def is_instructor(user):
    # Kullanıcının giriş yapmış olması ve bir Profile objesinin olması gerekir
    if not user.is_authenticated:
        return False
    # Profile objesi yoksa veya is_instructor alanı yoksa False döner
    if not hasattr(user, 'profile') or not hasattr(user.profile, 'is_instructor'):
        return False
    # Kullanıcının profilinde is_instructor True ise eğitmen kabul edilir
    return user.profile.is_instructor


@login_required
@user_passes_test(is_instructor)
def dashboard(request):
    """Eğitmen paneli ana sayfası"""
    egitmen = request.user
    
    # Süresi dolmayan veya end_date'i NULL olan öğrencileri çekiyoruz
    current_date = date.today()
    all_ogrenciler_raw = InstructorStudent.objects.filter(instructor=egitmen).select_related('student')
    
    active_ogrenciler = all_ogrenciler_raw.filter(Q(end_date__isnull=True) | Q(end_date__gte=current_date))

    query = request.GET.get('q')
    class_filter = request.GET.get('class_filter')
    
    display_ogrenciler = active_ogrenciler

    if class_filter and class_filter != 'all':
        if class_filter in SINIF_KATEGORILERI:
            classes_to_filter = SINIF_KATEGORILERI[class_filter]
            display_ogrenciler = display_ogrenciler.filter(student_class__in=classes_to_filter)
        else:
            messages.warning(request, "Geçersiz sınıf kategorisi seçildi.")

    if query:
        filtered_results_by_query = display_ogrenciler.filter(
            Q(student__first_name__icontains=query) |
            Q(student__last_name__icontains=query) |
            Q(student__username__icontains=query)
        )
        
        if not filtered_results_by_query.exists() and query:
            messages.info(request, f"'{query}' araması için öğrenci bulunamadı. Filtrelenmiş diğer öğrenciler gösteriliyor.")
        else:
            display_ogrenciler = filtered_results_by_query

    for relation in display_ogrenciler:
        relation.student_class_category = _get_class_category(relation.student_class)

    class_options_for_assignment = list(range(1, 13)) 

    context = {
        'ogrenciler': display_ogrenciler,
        'query': query,
        'class_options_for_assignment': class_options_for_assignment,
        'class_filter_options': [
            {'value': 'all', 'label': 'Tümü'},
            {'value': 'ilkokul', 'label': 'İlkokul'},
            {'value': 'ortaokul', 'label': 'Ortaokul'},
            {'value': 'lise', 'label': 'Lise'},
        ],
        'selected_class_filter': class_filter,
    }
    return render(request, "instructor/dashboard.html", context)


@login_required
@user_passes_test(is_instructor)
def ogrencilerim_listesi(request):
    """Eğitmenin eklediği öğrencileri gösterir"""
    egitmen = request.user
    ogrenciler = (
        InstructorStudent.objects
        .filter(instructor=egitmen)
        .select_related("student")
    )
    for relation in ogrenciler:
        relation.student_class_category = _get_class_category(relation.student_class)
    return render(request, "instructor/ogrencilerim.html", {"ogrenciler": ogrenciler})

@login_required
@user_passes_test(is_instructor)
def ogrenci_ekle(request):
    """Eğitmenin öğrenci listesine yeni öğrenci eklemesini sağlar"""
    egitmen = request.user

    try:
        from shop.models import Purchase
        satin_alanlar = (
            Purchase.objects
            .filter(product__role="student", paid=True)
            .values_list("user_id", flat=True)
        )
        all_possible_students = User.objects.filter(id__in=satin_alanlar)
    except ImportError:
        all_possible_students = User.objects.filter(is_active=True)
        messages.warning(request, "Shop.Purchase modeli bulunamadı. Öğrenci filtrelemesi varsayılan ayarlarla yapılıyor olabilir.")

    current_date = date.today()
    active_instructor_student_relations = InstructorStudent.objects.filter(
        Q(end_date__isnull=True) | Q(end_date__gte=current_date)
    )
    actively_assigned_student_ids = active_instructor_student_relations.values_list('student_id', flat=True)

    ogrenci_queryset = all_possible_students.exclude(
        Q(id__in=actively_assigned_student_ids) | Q(id=egitmen.id)
    )

    if request.method == "POST":
        form = EgitmenOgrenciEkleForm(request.POST)
        form.fields["ogrenci"].queryset = ogrenci_queryset
        if form.is_valid():
            ogrenci = form.cleaned_data["ogrenci"]
            duration_months_str = form.cleaned_data["duration_months"] # String olarak alabilir
            
            try:
                # duration_months değerini açıkça tam sayıya çevir
                duration_months = int(duration_months_str) 

                instructor_student_instance, created = InstructorStudent.objects.get_or_create(
                    instructor=egitmen, 
                    student=ogrenci,
                    defaults={'duration_months': duration_months} # defaults'ta int kullan
                )

                if not created: 
                    instructor_student_instance.duration_months = duration_months
                    instructor_student_instance.end_date = date.today() + relativedelta(months=+duration_months)
                    instructor_student_instance.save()
                    messages.success(request, f"Öğrenci '{ogrenci.username}' aboneliği başarıyla güncellendi.")
                else:
                    messages.success(request, f"Öğrenci '{ogrenci.username}' başarıyla eklendi.")

                return redirect("instructor:ogrencilerim_listesi")
            except ValueError:
                messages.error(request, "Abonelik süresi geçerli bir sayı olmalıdır.")
                # Formu tekrar göstermek için context ile render edilebilir
                return render(request, "instructor/ogrenci_ekle.html", {"form": form})
            except IntegrityError:
                messages.error(request, "Bu öğrenci zaten listenizde bulunuyor veya başka bir hata oluştu.")
                return render(request, "instructor/ogrenci_ekle.html", {"form": form})
            except Exception as e:
                messages.error(request, f"Öğrenci eklenirken/güncellenirken beklenmeyen bir hata oluştu: {e}")
                return render(request, "instructor/ogrenci_ekle.html", {"form": form})
        else:
            messages.error(request, "Formda hatalar var. Lütfen formu kontrol edin.")
    else:
        form = EgitmenOgrenciEkleForm()
    
    form.fields["ogrenci"].queryset = ogrenci_queryset

    return render(request, "instructor/ogrenci_ekle.html", {"form": form})


@login_required
@user_passes_test(is_instructor)
def egitimler(request):
    return render(request, 'instructor/egitimler.html')

@login_required
@user_passes_test(is_instructor)
def egzersizler(request):
    return render(request, 'instructor/egzersizler.html')

@login_required
@user_passes_test(is_instructor)
def testler(request):
    return render(request, 'instructor/testler.html')


@login_required
@user_passes_test(is_instructor)
def ogrenci_detay(request, ogrenci_id):
    ogrenci = get_object_or_404(User, id=ogrenci_id)

    # --- İSTATİSTİK HESAPLAMA KODU (MEVCUT) ---
    today = date.today()
    daily_attempts = GameAttempt.objects.filter(user=ogrenci, timestamp__date=today)
    daily_stats = daily_attempts.aggregate(
        total_score=Sum('score'),
        correct_sum=Sum('correct_answers'),
        wrong_sum=Sum('wrong_answers')
    )
    all_time_attempts = GameAttempt.objects.filter(user=ogrenci)
    all_time_stats = all_time_attempts.aggregate(
        total_score=Sum('score'),
        correct_sum=Sum('correct_answers'),
        wrong_sum=Sum('wrong_answers')
    )
    stats_data = {
        'daily': daily_stats,
        'all_time': all_time_stats,
        'games_played_today': daily_attempts.count(),
        'total_games_played': all_time_attempts.count(),
    }
    
    # --- MEVCUT KODUNUZ KORUNUYOR ---
    kurs_ilerlemeleri_queryset = KursIlerleme.objects.filter(ogrenci=ogrenci)
    egzersizler = EgzersizKaydi.objects.filter(ogrenci=ogrenci).order_by('-tarih')
    odevler = OdevDurumu.objects.filter(ogrenci=ogrenci)

    egitim_ilerlemeleri_takip_sekmesi = []
    for kurs_ilerleme_obj in kurs_ilerlemeleri_queryset: 
        kurs_adi = kurs_ilerleme_obj.ad
        toplam_gun = 30 
        bitirilen_gun = int(toplam_gun * (kurs_ilerleme_obj.ilerleme / 100))
        egitim_ilerlemeleri_takip_sekmesi.append({
            'kurs_adi': kurs_adi,
            'toplam_gun': toplam_gun,
            'bitirilen_gun': bitirilen_gun,
            'ilerleme_yuzdesi': kurs_ilerleme_obj.ilerleme,
            'durum': kurs_ilerleme_obj.durum,
        })

    assigned_courses = AssignedCourse.objects.filter(student=ogrenci, instructor=request.user).select_related('course')

    assign_course_form = AssignCourseForm()
    assign_course_form.fields['student'].queryset = User.objects.filter(id=ogrenci_id)
    assign_course_form.fields['student'].initial = ogrenci_id 

    devam_eden_kurs_sayisi = ogrenci.my_assigned_courses.filter(completed_days__lt=F('course__total_days')).count()
    toplam_atanan_urun_sayisi = ogrenci.assigned_products_to_student.count()

    instructor_student_relation_obj = InstructorStudent.objects.filter(instructor=request.user, student=ogrenci).first()
    
    # --- CANLI DERS İŞLEMLERİ (MEVCUT) ---
    plan_lesson_form = LiveLessonForm(initial={'student': ogrenci.id, 'instructor': request.user.id})
    lessons = LiveLesson.objects.filter(student=ogrenci).order_by('start_time')

    

    if request.method == 'POST':
        # Canlı ders planlama formu gönderimi
        if 'plan_lesson_submit' in request.POST:
            plan_lesson_form = LiveLessonForm(request.POST) 
            if plan_lesson_form.is_valid():
                lesson = plan_lesson_form.save(commit=False)
                lesson.student = ogrenci
                lesson.instructor = request.user
                lesson.save()
                messages.success(request, "Canlı ders başarıyla planlandı.")
                return redirect(f"{request.path_info}#canli-derslerim")
            else:
                messages.error(request, "Canlı ders planlanırken bir hata oluştu. Lütfen formu kontrol edin.")
        
       

    # --- CONTEXT VERİLERİ ---
    context = {
        'ogrenci': ogrenci,
        'kurs_ilerlemeleri': kurs_ilerlemeleri_queryset,
        'egzersizler': egzersizler,
        'odevler': odevler,
        'egitim_ilerlemeleri': egitim_ilerlemeleri_takip_sekmesi,
        'assigned_courses': assigned_courses,
        'assign_course_form': assign_course_form,
        'devam_eden_kurs_sayisi': devam_eden_kurs_sayisi,
        'toplam_atanan_urun_sayisi': toplam_atanan_urun_sayisi,
        'today': date.today(),
        'instructor_student_relation': instructor_student_relation_obj,
        'stats': stats_data,
        
        'plan_lesson_form': plan_lesson_form,
        'lessons': lessons,
        
    }
    return render(request, 'instructor/ogrenci_detay.html', context)




@login_required
@user_passes_test(is_instructor)
@require_POST
def assign_course_to_student(request, ogrenci_id):
    """
    Öğrenciye kurs atama işlemini yapar.
    Sadece eğitmenin öğrencisine kurs atamasını sağlar.
    """
    egitmen = request.user
    ogrenci = get_object_or_404(User, id=ogrenci_id)

    form = AssignCourseForm(request.POST)
    form.fields['student'].queryset = User.objects.filter(id=ogrenci_id, assigned_instructor__instructor=egitmen)

    if form.is_valid():
        selected_student = form.cleaned_data['student']
        selected_course = form.cleaned_data['course']

        if not InstructorStudent.objects.filter(instructor=egitmen, student=selected_student).exists():
            messages.error(request, "Bu öğrenci size atanmamış. Kurs atama yetkiniz yok.")
            return redirect('instructor:ogrenci_detay', ogrenci_id=ogrenci_id)

        try:
            AssignedCourse.objects.create(
                instructor=egitmen,
                student=selected_student,
                course=selected_course
            )
            messages.success(request, f"'{selected_course.title}' kursu '{selected_student.username}' öğrencisine başarıyla atandı.")
        except IntegrityError:
            messages.warning(request, f"'{selected_student.username}' öğrencisine '{selected_course.title}' kursu zaten atanmış.")
        except Exception as e:
            messages.error(request, f"Kurs atanırken bir hata oluştu: {e}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Hata ({field}): {error}")

    return redirect('instructor:ogrenci_detay', ogrenci_id=ogrenci_id)


@login_required
@user_passes_test(is_instructor)
@require_POST
def unassign_course_from_student(request, assigned_course_id):
    """
    Öğrenciye atanan kursu geri alır (siler).
    """
    egitmen = request.user
    assigned_course = get_object_or_404(AssignedCourse, id=assigned_course_id, instructor=egitmen)
    
    student_id = assigned_course.student.id 

    try:
        assigned_course.delete()
        messages.success(request, f"'{assigned_course.course.title}' kursu '{assigned_course.student.username}' öğrencisinden başarıyla kaldırıldı.")
    except Exception as e:
        messages.error(request, f"Kurs kaldırılırken bir hata oluştu: {e}")
    
    return redirect('instructor:ogrenci_detay', ogrenci_id=student_id)

@require_POST
@login_required
@user_passes_test(is_instructor)
def ogrenci_cikar(request, student_id):
    egitmen = request.user
    try:
        iliski = InstructorStudent.objects.get(instructor=egitmen, student_id=student_id)
        iliski.delete()
        messages.success(request, "Öğrenci başarıyla çıkarıldı.")
    except InstructorStudent.DoesNotExist:
        messages.warning(request, "Bu öğrenci listenizde bulunmuyor.")
    return redirect("instructor:ogrencilerim_listesi")

@login_required
@user_passes_test(is_instructor)
def assign_student_class(request, student_id):
    """
    Öğrenciye sınıf atama işlemini yapar.
    """
    egitmen = request.user
    try:
        relation = InstructorStudent.objects.get(instructor=egitmen, student__id=student_id)
        selected_class = request.POST.get('student_class') 

        if selected_class and selected_class.isdigit(): 
            relation.student_class = int(selected_class)
            relation.save()
            messages.success(request, f"{relation.student.username} öğrencisine sınıf başarıyla atandı.")
        else:
            messages.error(request, "Geçersiz sınıf değeri.")
    except InstructorStudent.DoesNotExist:
        messages.error(request, "Bu öğrenci listenizde bulunmuyor veya yetkiniz yok.")
    
    return redirect('instructor:dashboard')

@login_required
def logout_view(request):
    """Kullanıcıyı oturumdan çıkarır ve ana sayfaya yönlendirir."""
    logout(request)
    messages.info(request, "Başarıyla çıkış yaptınız.")
    return redirect('index')


# --- Yeni Profil View'ları ---

@login_required
def profile_view(request):
    user_profile = request.user.profile
    
    form = ProfileUpdateForm(instance=user_profile, initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name
    })

    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'instructor/profile.html', context)


@login_required
def profile_update_view(request):
    if request.method == 'POST':
        user_profile = request.user.profile
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi.')
            return redirect('instructor:profile_view')
        else:
            messages.error(request, 'Profil güncellenirken bir hata oluştu. Lütfen formu kontrol edin.')
            return render(request, 'instructor/profile.html', {'form': form, 'user': request.user})
    else:
        return redirect('instructor:profile_view')


# --- YENİ SİPARİŞ VE KREDİ SİSTEMİ VIEW FONKSİYONLARI ---

@login_required
@user_passes_test(is_instructor)
def instructor_new_order(request): # create_new_order_page yerine bu isim kullanıldı
    """
    Eğitmenin yeni sipariş oluşturacağı, ürünleri listeleyip sepete ekleyeceği sayfa.
    """
    products = Product.objects.filter(is_active=True).order_by('price')
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity
        })
        cart_total += product.price * quantity

    context = {
        'products': products,
        'cart_items': cart_items,
        'cart_total': cart_total,
    }
    return render(request, 'instructor/instructor_new_order.html', context) # Şablon adı güncellendi

@login_required
@user_passes_test(is_instructor)
@require_POST
def add_to_cart(request, product_id):
    """
    Ürünü sepete ekleme (AJAX ile çağrılabilir).
    """
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    cart_key = str(product_id)
    if cart_key in cart:
        cart[cart_key] += 1
    else:
        cart[cart_key] = 1
    
    request.session['cart'] = cart
    messages.success(request, f"{product.name} sepete eklendi.")
    return redirect('instructor:instructor_new_order')


@login_required
@user_passes_test(is_instructor)
@require_POST
def remove_from_cart(request, product_id):
    """
    Ürünü sepetten çıkarma (AJAX ile çağrılabilir).
    """
    cart = request.session.get('cart', {})
    cart_key = str(product_id)
    
    # Bayrak kullanarak mesajın ne zaman verileceğini belirleyelim
    product_found = False 

    if cart_key in cart:
        product_found = True # Ürün bulundu
        if cart[cart_key] > 1:
            cart[cart_key] -= 1
        else:
            del cart[cart_key]
        
        request.session['cart'] = cart # Sepeti her durumda güncelle
        messages.info(request, f"Ürün sepetten çıkarıldı.") # Ürün çıkarıldığında mesaj ver
    else:
        messages.error(request, "Ürün sepette bulunamadı.")
    
    return redirect('instructor:instructor_new_order')


@login_required
@user_passes_test(is_instructor)
@require_POST
def purchase_product(request):
    """
    Sepetteki ürünleri Stripe ile ödeme işlemi.
    DÜZENLENMİŞ VERSİYON: Her ürün adedi için ayrı Order kaydı oluşturur.
    """
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Sepetiniz boş, lütfen önce ürün ekleyin.")
        return redirect('instructor:instructor_new_order')

    cart_total_decimal = 0
    order_items_details = [] 
    for product_id_str, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id_str))
        cart_total_decimal += product.price * quantity
        order_items_details.append({'product': product, 'quantity': quantity})

    amount_cents = int(cart_total_decimal * 100) 

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'try',
                        'product_data': {
                            'name': 'Kredi Satın Alımı',
                            'description': f"Toplam {sum(item['quantity'] for item in order_items_details)} adet ürün",
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('instructor:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('instructor:payment_cancel')),
            metadata={
                'instructor_id': request.user.id,
                'cart_data': str(cart) # metadata'da sepet verisini saklamak hala iyi bir fikir.
            }
        )

        with transaction.atomic():
            for item in order_items_details:
                product = item['product']
                quantity = item['quantity']
                
                # 'quantity' kadar döngüye girerek her bir ürün için ayrı bir Order kaydı oluşturuyoruz.
                for _ in range(quantity):
                    Order.objects.create(
                        instructor=request.user,
                        product=product,
                        amount=product.price,  # Artık her kaydın tutarı, ürünün tekil fiyatıdır.
                        quantity=1,            # Her kaydın adedi her zaman 1'dir.
                        is_paid=False,
                        stripe_charge_id=checkout_session.id,
                        is_used_for_assignment=False
                    )
        
        request.session['cart'] = {}
        messages.info(request, "Ödeme sayfasına yönlendiriliyorsunuz...")

        return redirect(checkout_session.url, code=303)

    except Exception as e:
        messages.error(request, f"Beklenmeyen bir hata oluştu: {e}")
        return redirect('instructor:instructor_new_order')

@login_required
@user_passes_test(is_instructor)
def payment_success(request):
    messages.success(request, "Ödemeniz başarıyla alındı! Kredileriniz hesabınıza ekleniyor...")
    
    session_id = request.GET.get('session_id')

    try:
        with transaction.atomic():
            orders_to_update = Order.objects.filter(
                instructor=request.user,
                is_paid=False,
                stripe_charge_id=session_id
            )
            
            if not orders_to_update.exists():
                if not session_id:
                    messages.error(request, "Ödeme oturumu bilgisi (session_id) alınamadı. Kredi eklenmedi.")
                else:
                    messages.error(request, f"'{session_id}' ID'li ödeme oturumu için işlenecek sipariş bulunamadı veya zaten işlenmiş. Kredi eklenmedi.")
                return render(request, 'instructor/payment_success.html')

            total_credits_to_add = 0
            
            for order in orders_to_update:
                try:
                    checkout_session = stripe.checkout.Session.retrieve(order.stripe_charge_id)
                    
                    if checkout_session.payment_status == "paid":
                        if not order.is_paid:
                            order.is_paid = True
                            order.save()
                            total_credits_to_add += order.quantity # Her bir ürün adedi kadar kredi ekle (subscription_months artık kullanılmıyor)
                            messages.info(request, f"Sipariş {order.id} için {order.quantity} kredi eklendi.") # Debug mesajı

                    else:
                        messages.warning(request, f"Sipariş ID {order.id} için Stripe ödeme durumu 'paid' değil. Durum: {checkout_session.payment_status}. Kredi eklenmedi.")
                except stripe.error.StripeError as e:
                    messages.error(request, f"Stripe oturumu alınırken hata (Sipariş ID {order.id}): {e._message}. Kredi eklenmedi.")
                    continue
                except Exception as e:
                    messages.error(request, f"Sipariş ID {order.id} işlenirken beklenmeyen hata: {e}. Kredi eklenmedi.")
                    continue

            if total_credits_to_add > 0:
                credit_account, created = Credit.objects.get_or_create(instructor=request.user)
                credit_account.amount += total_credits_to_add
                credit_account.save()
                messages.success(request, f"Kredileriniz başarıyla eklendi: {total_credits_to_add} adet.")
            else:
                messages.info(request, "Bu ödeme için kredi eklenmedi.")

    except Exception as e:
        messages.error(request, f"Kredi eklenirken genel bir hata oluştu: {e}")

    return render(request, 'instructor/payment_success.html')


@login_required
@user_passes_test(is_instructor)
def payment_cancel(request):
    """
    Stripe ödemesi iptal edildiğinde kullanıcıyı yönlendireceğimiz sayfa.
    """
    messages.info(request, "Ödeme işlemi iptal edildi.")
    return render(request, 'instructor/payment_cancel.html')


@login_required
@user_passes_test(is_instructor)
def instructor_order_history(request): # order_history yerine bu isim kullanıldı
    """
    Eğitmenin geçmiş siparişlerini görüntülediği sayfa.
    """
    orders = Order.objects.filter(instructor=request.user).order_by('-order_date')
    context = {
        'orders': orders
    }
    return render(request, 'instructor/instructor_order_history.html', context) # Şablon adı güncellendi

@login_required
@user_passes_test(is_instructor)
def instructor_payment_notifications(request):
    """Eğitmen panelinde ödeme bildirimleri sayfası (Placeholder)"""
    # Buraya Stripe webhook'larından gelen bildirimleri listeleyebilirsiniz.
    # Şimdilik sadece bir placeholder olarak kalacak.
    return render(request, "instructor/instructor_payment_notifications.html", {})


@login_required
@user_passes_test(is_instructor)
def my_credits(request):
    """
    Eğitmenin sahip olduğu kredileri ve atanan ürünleri görüntülediği sayfa.
    Buradan kredi kullanma (öğrenciye atama) işlemi yapılacak.
    """
    credit_account, created = Credit.objects.get_or_create(instructor=request.user)
    available_credits = credit_account.amount

    instructor_students = InstructorStudent.objects.filter(instructor=request.user).select_related('student')
    students = [is_obj.student for is_obj in instructor_students]
    
    assigned_products = AssignedProduct.objects.filter(instructor=request.user).select_related('student', 'product').order_by('-assigned_date')

    # YENİ FİLTRELEME: Dropdown'da sadece eğitmenin satın aldığı ve henüz atanmamış kredi birimlerini göster
    available_orders_for_assignment = Order.objects.filter(
        instructor=request.user, 
        is_paid=True, 
        is_used_for_assignment=False # Henüz atanmamış olanları getir
    ).select_related('product').order_by('product__name', 'order_date')

    context = {
        'available_credits': available_credits,
        'students': students,
        'assigned_products': assigned_products,
        'available_orders_for_assignment': available_orders_for_assignment, # Yeni context değişkeni
    }
    return render(request, 'instructor/my_credits.html', context)


@login_required
@user_passes_test(is_instructor)
@require_POST
def use_credit(request):
    """
    Eğitmenin kredisini kullanarak bir ürünü öğrenciye atadığı view. (POST isteği)
    Şimdi kredi, Order objeleri üzerinden yönetilecek.
    """
    order_id_to_use = request.POST.get('order_id') # product_id yerine order_id alacağız
    student_id = request.POST.get('student_id')

    try:
        with transaction.atomic():
            # Kullanılacak Order objesini bul
            order_to_use = get_object_or_404(Order, 
                                             id=order_id_to_use, 
                                             instructor=request.user, 
                                             is_paid=True, 
                                             is_used_for_assignment=False)

            # Eğitmenin kredi hesabını kontrol et (Credit.amount hala genel toplamı tutuyor)
            credit_account = get_object_or_404(Credit, instructor=request.user)
            if credit_account.amount <= 0:
                messages.error(request, "Yeterli krediniz bulunmamaktadır.")
                return redirect('instructor:my_credits')

            product = order_to_use.product # Atanacak ürün, Order objesinden geliyor
            student = get_object_or_404(User, id=student_id)

            # Öğrencinin gerçekten bu eğitmene ait olup olmadığını kontrol et (güvenlik)
            instructor_student_relation = get_object_or_404(InstructorStudent, instructor=request.user, student=student)

            # Krediyi düş (bu genel krediden 1 düşecek, çünkü bir Order birimi kullanıyoruz)
            credit_account.amount -= 1
            credit_account.save()

            # Order'ı "kullanıldı" olarak işaretle
            order_to_use.is_used_for_assignment = True
            order_to_use.save()

            # Ürünü öğrenciye ata
            AssignedProduct.objects.create(
                instructor=request.user,
                student=student,
                product=product,
                is_used=True # AssignedProduct'taki is_used alanı
            )

            # ABONELİK SÜRESİNİ GÜNCELLEME KISMI (Order'daki product'ın subscription_months'ı kadar)
            # Bu kısım mağazadan alınan ürünün abonelik özelliği varsa çalışır, krediyle alakası yok.
            if product.subscription_months > 0:
                if not instructor_student_relation.end_date or instructor_student_relation.end_date < date.today():
                    instructor_student_relation.end_date = date.today() + relativedelta(months=+product.subscription_months)
                else:
                    instructor_student_relation.end_date += relativedelta(months=+product.subscription_months)
                
                instructor_student_relation.save()
                messages.success(request, f"'{product.name}' ürünü '{student.username}' öğrencisine başarıyla atandı ve abonelik süresi {product.subscription_months} ay uzatıldı. Krediniz güncellendi.")
            else:
                messages.success(request, f"'{product.name}' ürünü '{student.username}' öğrencisine başarıyla atandı. Krediniz güncellendi.")
            
            return redirect('instructor:my_credits')

    except Order.DoesNotExist:
        messages.error(request, "Geçersiz veya kullanılamaz ürün seçimi. Lütfen tekrar deneyin.")
    except User.DoesNotExist:
        messages.error(request, "Geçersiz öğrenci seçimi. Lütfen tekrar deneyin.")
    except InstructorStudent.DoesNotExist:
        messages.error(request, "Bu öğrenci sizin öğrencileriniz arasında bulunmuyor veya yetkiniz yok.")
    except Exception as e:
        messages.error(request, f"Kredi kullanılırken genel bir hata oluştu: {e}")
        
    messages.error(request, "Geçersiz istek.")
    return redirect('instructor:my_credits')


@login_required
@user_passes_test(is_instructor)
def schedule_live_lesson(request, student_id):
    student = get_object_or_404(User, id=student_id)
    if request.method == 'POST':
        form = LiveLessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.instructor = request.user
            lesson.student = student
            lesson.save()
            messages.success(request, f"{student.username} için canlı ders başarıyla planlandı.")
            return redirect('instructor:ogrenci_detay', ogrenci_id=student_id)
    else:
        form = LiveLessonForm()

    context = {
        'form': form,
        'student': student
    }
    return render(request, 'instructor/schedule_live_lesson.html', context)

@login_required
@user_passes_test(is_instructor)
def list_live_lessons(request):
    # Eğitmenin gelecekteki ve henüz tamamlanmamış tüm derslerini listele
    lessons = LiveLesson.objects.filter(
        instructor=request.user,
        start_time__gte=timezone.now(),
        is_completed=False
    ).select_related('student').order_by('start_time')

    context = {
        'lessons': lessons
    }
    return render(request, 'instructor/list_live_lessons.html', context)