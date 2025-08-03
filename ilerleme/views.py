from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import transaction

from egitimler.models import Ders
from satinalim.models import SatinAlim
from .models import DersTamamlama

@login_required
@transaction.atomic                      #  ← veritabanı kilitlerini azaltır
def dersi_tamamla(request, ders_id):
    if request.method != "POST":
        # GET gelirse doğrudan dersi göster
        return redirect("egitim_detay", egitim_id=ders_id)

    ders = get_object_or_404(Ders, id=ders_id)

    # 1. DersTamamlama kaydı
    tamamlama, _ = DersTamamlama.objects.get_or_create(
        kullanici=request.user,
        ders=ders,
        defaults={"tamamlandi": True},
    )
    if not tamamlama.tamamlandi:
        tamamlama.tamamlandi = True
        tamamlama.save(update_fields=["tamamlandi"])

    # 2. Yüzde hesapla
    toplam    = ders.egitim.dersler.count()
    tamamlanan = DersTamamlama.objects.filter(
        kullanici=request.user,
        ders__egitim=ders.egitim,
        tamamlandi=True,
    ).count()
    oran = int((tamamlanan / toplam) * 100) if toplam else 0

    # 3. SatinAlim güncelle
    SatinAlim.objects.update_or_create(
        kullanici=request.user,
        egitim=ders.egitim,
        defaults={"ilerleme_orani": oran},
    )

    # 4. AJAX ise JSON döndür
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"basarili": True, "ilerleme": oran})

    # 5. Geldiği sayfaya geri dön (HTTP_REFERER)
    next_url = request.META.get("HTTP_REFERER") or reverse("egitim_detay", args=[ders.egitim.id])
    return HttpResponseRedirect(next_url)
