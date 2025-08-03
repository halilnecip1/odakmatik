from django.shortcuts import render,  get_object_or_404, redirect
from shop.models import Product, Purchase # Bu importlar zaten vardı
from .models import Makale
from django.core.mail import send_mail
from django.conf import settings

def index(request):
    products = Product.objects.all()

    # Kullanıcı giriş yaptıysa satın aldığı rolleri topla
    owned_roles = set()
    if request.user.is_authenticated:
        owned_roles = set(
            Purchase.objects.filter(user=request.user, paid=True)
            .values_list('product__role', flat=True)
        )

    return render(request, 'anasayfa/index.html', {
        'products': products,
        'owned_roles': owned_roles,
    })


def iletisim(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Form doğrulama (basit bir örnek)
        if not name or not email or not message:
            return render(request, 'anasayfa/iletisim.html', {
                'error_message': 'Lütfen tüm alanları doldurunuz.',
                'name': name,
                'email': email,
                'message': message
            })
        
        # E-posta içeriği
        subject = f'Odak Matik İletişim Formu - {name}'
        email_message = f'Ad Soyad: {name}\nE-posta: {email}\n\nMesaj:\n{message}'
        
        # E-posta gönderme
        try:
            send_mail(
                subject, # E-posta konusu
                email_message, # E-posta içeriği (düz metin)
                settings.DEFAULT_FROM_EMAIL, # Kimden (settings.py'den gelir)
                ['halilnecip25@outlook.com'], # Kime (buraya mesajların gelmesini istediğiniz e-posta adresini yazın)
                fail_silently=False, # Hata olursa traceback göster
            )
            return render(request, 'anasayfa/iletisim.html', {'success_message': 'Mesajınız başarıyla gönderildi!'})
        except Exception as e:
            # E-posta gönderme hatası
            return render(request, 'anasayfa/iletisim.html', {
                'error_message': f'Mesaj gönderilirken bir hata oluştu: {e}',
                'name': name,
                'email': email,
                'message': message
            })

    return render(request, 'anasayfa/iletisim.html')


def articles(request): # YENİ FONKSİYON
    return render(request, 'articles.html')

def about(request): # YENİ FONKSİYON
    return render(request, 'about.html')

def references(request): # YENİ FONKSİYON
    return render(request, 'references.html')

def kvkk(request): # YENİ FONKSİYON
    return render(request, 'kvkk.html')

def terms_of_service(request): # YENİ FONKSİYON
    return render(request, 'terms_of_service.html')


def articles(request): # <<<< Buradaki fonksiyon adını 'articles' olarak değiştirin
    makaleler = Makale.objects.all().order_by('-yayinlanma_tarihi')
    return render(request, 'articles.html', {'makaleler': makaleler})

def makale_detay(request, slug):
    # Belirli bir slug'a sahip makaleyi getir, yoksa 404 hatası döndür
    makale = get_object_or_404(Makale, slug=slug)
    return render(request, 'makale_detay.html', {'makale': makale}) # templates/makale_detay.html'e gidiyor