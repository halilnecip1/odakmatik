# shop/views.py
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q # Yeni eklendi
from django.http import HttpResponseForbidden, Http404 # Yeni eklendi
from .models import Product, Purchase, Kitap, KitapSatınAlım, Oyun, OyunSatınAlım # Yeni modeller eklendi
from instructor.models import Profile

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required(login_url='login')
def home(request):
    # Yazılımlar
    products = Product.objects.all()
    # Kullanıcının sahip olduğu yazılımlar
    purchases = Purchase.objects.filter(user=request.user, paid=True)
    owned_roles = {p.product.role for p in purchases}

    # Kitaplar
    kitaplar = Kitap.objects.all().order_by('baslik') # Alfabetik sıralama
    # Kullanıcının sahip olduğu kitaplar
    satinalinan_kitaplar = KitapSatınAlım.objects.filter(user=request.user, odendi=True)
    owned_kitap_slugs = {k.kitap.slug for k in satinalinan_kitaplar}

    # Oyunlar
    oyunlar = Oyun.objects.all().order_by('baslik') # Alfabetik sıralama
    # Kullanıcının sahip olduğu oyunlar
    satinalinan_oyunlar = OyunSatınAlım.objects.filter(user=request.user, odendi=True)
    owned_oyun_slugs = {o.oyun.slug for o in satinalinan_oyunlar}

    context = {
        'products': products,
        'owned_roles': owned_roles,
        'kitaplar': kitaplar,
        'owned_kitap_slugs': owned_kitap_slugs,
        'oyunlar': oyunlar,
        'owned_oyun_slugs': owned_oyun_slugs,
    }
    return render(request, 'shop/home.html', context)


# Kayıtlı olmayanı uyar
from django.views.decorators.http import require_GET

@require_GET
def public_home(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    products = Product.objects.all()
    kitaplar = Kitap.objects.all().order_by('baslik')
    oyunlar = Oyun.objects.all().order_by('baslik')

    # Public home sayfasında satın alınmış ürünleri göstermeye gerek yok
    # Sadece ürünleri listeleriz, giriş yapmaları gerektiği belirtilir.
    return render(request, 'shop/public_home.html', {
        'products': products,
        'kitaplar': kitaplar,
        'oyunlar': oyunlar,
    })


# Satın alma başlat (Hem yazılım, hem kitap, hem oyun için tek bir fonksiyon)
@login_required
def create_checkout(request, product_type, slug):
    # product_type: 'yazilim', 'kitap', 'oyun'
    # slug: Ürünün benzersiz slug'ı veya yazılımlar için 'role'

    product_obj = None
    purchase_obj = None
    title = ""
    price_cents = 0

    if product_type == 'yazilim':
        product_obj = get_object_or_404(Product, role=slug)
        purchase_obj, _ = Purchase.objects.get_or_create(user=request.user, product=product_obj, paid=False)
        title = product_obj.title
        price_cents = product_obj.price_cents
        success_url_name = 'shop:success'
    elif product_type == 'kitap':
        product_obj = get_object_or_404(Kitap, slug=slug)
        purchase_obj, _ = KitapSatınAlım.objects.get_or_create(user=request.user, kitap=product_obj, odendi=False)
        title = product_obj.baslik
        price_cents = product_obj.fiyat_kurus
        success_url_name = 'shop:success'
    elif product_type == 'oyun':
        product_obj = get_object_or_404(Oyun, slug=slug)
        purchase_obj, _ = OyunSatınAlım.objects.get_or_create(user=request.user, oyun=product_obj, odendi=False)
        title = product_obj.baslik
        price_cents = product_obj.fiyat_kurus
        success_url_name = 'shop:success'
    else:
        raise Http404("Geçersiz ürün tipi.")

    if not product_obj:
        raise Http404("Ürün bulunamadı.")
    
    # Eğer ürün zaten satın alınmışsa ve ödenmişse, tekrar ödeme almayı engelle
    if (product_type == 'yazilim' and purchase_obj.paid) or \
       (product_type == 'kitap' and purchase_obj.odendi) or \
       (product_type == 'oyun' and purchase_obj.odendi):
        return redirect('shop:home') # Zaten satın alınmışsa ana sayfaya yönlendir

    checkout_session = stripe.checkout.Session.create(
        customer_email=request.user.email,
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'try',
                'unit_amount': price_cents,
                'product_data': {'name': title},
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse(success_url_name)) + f'?session_id={{CHECKOUT_SESSION_ID}}&product_type={product_type}&slug={slug}',
        cancel_url=request.build_absolute_uri(reverse('shop:home')),
    )
    
    # Satın alma objesinin stripe_session_id'sini güncelle
    purchase_obj.stripe_session_id = checkout_session.id
    purchase_obj.save()
    return redirect(checkout_session.url)


@login_required
def success(request):
    session_id = request.GET.get('session_id')
    product_type = request.GET.get('product_type')
    slug = request.GET.get('slug')

    if not all([session_id, product_type, slug]):
        return redirect('shop:home')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        return redirect('shop:home')

    if session.payment_status == 'paid':
        if product_type == 'yazilim':
            product = get_object_or_404(Product, role=slug)
            purchase = get_object_or_404(Purchase, stripe_session_id=session_id, user=request.user, product=product)
            
            if not purchase.paid:
                purchase.paid = True
                purchase.save()

            if purchase.product.role == 'instructor':
                try:
                    profile = request.user.profile
                    if not profile.is_instructor:
                        profile.is_instructor = True
                        profile.save()
                except Profile.DoesNotExist:
                    pass
        
        # ... (kitap ve oyun kodları) ...
        elif product_type == 'kitap':
            kitap = get_object_or_404(Kitap, slug=slug)
            purchase = get_object_or_404(KitapSatınAlım, stripe_session_id=session_id, user=request.user, kitap=kitap)
            if not purchase.odendi:
                purchase.odendi = True
                purchase.save()
        # ...

        # ... (render kısmı) ...
        if product_type == 'yazilim':
            purchased_item = purchase.product
        # ...
        return render(request, 'shop/success.html', {
            'purchase': purchase,
            'product_type': product_type,
            'purchased_item': purchased_item
        })
    else:
        return redirect('shop:home')


# Kitap içeriğine erişim view'ı
@login_required
def access_kitap(request, slug):
    kitap = get_object_or_404(Kitap, slug=slug)
    # Kullanıcının bu kitabı satın alıp almadığını kontrol et
    if not KitapSatınAlım.objects.filter(user=request.user, kitap=kitap, odendi=True).exists():
        return HttpResponseForbidden("Bu kitaba erişim izniniz yok.")
    
    if kitap.icerik_url:
        return redirect(kitap.icerik_url)
    # elif kitap.icerik_dosya: # Eğer dosya alanı kullanıyorsanız
    #     # Django'nun dosya sunmasını veya dosya indirilebilir linkini sağlamasını ayarlamalısınız
    #     # Örneğin:
    #     # from django.http import FileResponse
    #     # return FileResponse(kitap.icerik_dosya.open(), as_attachment=True, filename=kitap.icerik_dosya.name)
    else:
        raise Http404("Bu kitabın içeriği bulunamadı veya bir URL/dosya tanımlanmamış.")

# Oyun içeriğine erişim view'ı
@login_required
def access_oyun(request, slug):
    oyun = get_object_or_404(Oyun, slug=slug)
    # Kullanıcının bu oyunu satın alıp almadığını kontrol et
    if not OyunSatınAlım.objects.filter(user=request.user, oyun=oyun, odendi=True).exists():
        return HttpResponseForbidden("Bu oyuna erişim izniniz yok.")
    
    if oyun.indirme_url:
        return redirect(oyun.indirme_url)
    else:
        raise Http404("Bu oyunun indirme/erişim adresi bulunamadı.")