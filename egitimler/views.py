# benim_sitem/egitimler/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse # Bu zaten vardı, ama kullanımına dikkat!
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
import stripe
from django.contrib import messages
# from django.shortcuts import redirect # Zaten yukarıda tanımlı
from .models import Egitim, Ders
from satinalim.models import SatinAlim
from ilerleme.models import DersTamamlama

stripe.api_key = settings.STRIPE_SECRET_KEY


def egitim_listesi(request):
    egitimler = Egitim.objects.all()
    satin_alinanlar = []

    if request.user.is_authenticated:
        satin_alinanlar = list(
            SatinAlim.objects.filter(kullanici=request.user).values_list("egitim_id", flat=True)
        )

    context = {
        "egitimler": egitimler,
        "satin_alinanlar": satin_alinanlar,
    }
    return render(request, "egitimler/egitim_listesi.html", context)


@login_required
def egitim_detay(request, egitim_id):
    egitim = get_object_or_404(Egitim, id=egitim_id)
    satin_alindi = SatinAlim.objects.filter(kullanici=request.user, egitim=egitim).exists()
    dersler = Ders.objects.filter(egitim=egitim) if satin_alindi else []

    tamamlanan_idler = []
    ilerleme = 0
    if satin_alindi:
        tamamlanan_idler = list(DersTamamlama.objects.filter(
            kullanici=request.user, ders__egitim=egitim, tamamlandi=True
        ).values_list("ders_id", flat=True))
        toplam = dersler.count()
        ilerleme = int((len(tamamlanan_idler) / toplam) * 100) if toplam else 0

    context = {
        "egitim": egitim,
        "satin_alindi": satin_alindi,
        "dersler": dersler,
        "tamamlanan_dersler": tamamlanan_idler,
        "ilerleme": ilerleme,
    }
    return render(request, "egitimler/egitim_detay.html", context)

# from django.contrib import messages # Zaten yukarıda tanımlı
# from django.shortcuts import redirect # Zaten yukarıda tanımlı

@login_required
def ders_detay(request, ders_id):
    """Bir dersin detayını gösterir; kullanıcı o dersi içeren eğitimi satın almış olmalı."""
    ders = get_object_or_404(Ders, id=ders_id)

    satin_alindi = SatinAlim.objects.filter(kullanici=request.user, egitim=ders.egitim).exists()
    if not satin_alindi:
        messages.warning(request, "Bu derse erişim izniniz yok. Lütfen önce giriş yapınız veya eğitim satın alınız.")
        # Düzeltildi: 'kullanici:giris' zaten doğruydu, bu örnek bir düzeltme değildi.
        return redirect('kullanici:giris')

    return render(request, "egitimler/ders_detay.html", {"ders": ders})


@login_required
def satin_al(request, egitim_id):
    egitim = get_object_or_404(Egitim, id=egitim_id)
    satin_alindi_mi = SatinAlim.objects.filter(kullanici=request.user, egitim=egitim).exists()
    if not satin_alindi_mi:
        SatinAlim.objects.create(kullanici=request.user, egitim=egitim)
    # BURASI DÜZELTİLDİ: 'egitimler:' eklendi
    return redirect("egitimler:egitim_detay", egitim_id=egitim.id)


@login_required
def egitim_odemesi(request, egitim_id):
    egitim = get_object_or_404(Egitim, id=egitim_id)
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "try",
                    "product_data": {"name": egitim.baslik},
                    "unit_amount": int(egitim.fiyat * 100),  # kuruş cinsinden
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        # BURASI DÜZELTİLDİ: 'egitimler:' eklendi
        success_url=request.build_absolute_uri(reverse("egitimler:odeme_basarili", args=[egitim.id])),
        # BURASI DÜZELTİLDİ: 'egitimler:' eklendi
        cancel_url=request.build_absolute_uri(reverse("egitimler:egitim_detay", args=[egitim.id])),
        metadata={"egitim_id": str(egitim.id)},  # webhook için
        client_reference_id=egitim.id,
        customer_email=request.user.email,
    )
    return redirect(session.url, code=303)


@login_required
def odeme_basarili(request, egitim_id):
    egitim = get_object_or_404(Egitim, id=egitim_id)
    satin_alindi_mi = SatinAlim.objects.filter(kullanici=request.user, egitim=egitim).exists()
    if not satin_alindi_mi:
        SatinAlim.objects.create(kullanici=request.user, egitim=egitim)
    return render(request, "egitimler/odeme_basarili.html", {"egitim": egitim})


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    # Satın alma tamamlandıysa kullanıcının hesabına eğitimi tanımla
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session.get("customer_email")
        egitim_id = session.get("metadata", {}).get("egitim_id") or session.get("client_reference_id")

        if customer_email and egitim_id:
            from django.contrib.auth.models import User

            try:
                user = User.objects.get(email=customer_email)
                egitim = Egitim.objects.get(id=egitim_id)
                SatinAlim.objects.get_or_create(kullanici=user, egitim=egitim)
            except (User.DoesNotExist, Egitim.DoesNotExist):
                pass

    return HttpResponse(status=200)