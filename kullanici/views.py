# kullanici/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from satinalim.models import SatinAlim
from shop.models import KitapSatınAlım, OyunSatınAlım, Purchase # Purchase modelini de import et!

def kayit_ol(request):
    if request.method == 'POST':
        kullanici_adi = request.POST['kullanici_adi']
        email = request.POST['email']
        sifre = request.POST['sifre']
        try:
            user = User.objects.create_user(username=kullanici_adi, email=email, password=sifre)
            login(request, user)
            return redirect('/')
        except IntegrityError:
            return render(request, 'kullanici/kayit.html', {'hata': 'Bu kullanıcı adı zaten alınmış.'})
    return render(request, 'kullanici/kayit.html')


def giris_yap(request):
    if request.method == "POST":
        kullanici_adi = request.POST['kullanici_adi']
        sifre = request.POST['sifre']
        user = authenticate(request, username=kullanici_adi, password=sifre)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'kullanici/giris.html', {'hata': 'Hatalı bilgi girdiniz.'})
    return render(request, 'kullanici/giris.html')


def cikis_yap(request):
    logout(request)
    return redirect('/')

@login_required(login_url="/kullanici/giris/")
def profil(request):
    satin_almalar = SatinAlim.objects.filter(kullanici=request.user).select_related("egitim")
    
    # Satın alınan kitap, oyun ve YAZILIMLARI çekme
    satın_alinan_kitaplar = KitapSatınAlım.objects.filter(user=request.user, odendi=True).select_related('kitap')
    satın_alinan_oyunlar = OyunSatınAlım.objects.filter(user=request.user, odendi=True).select_related('oyun')
    # YENİ EKLENECEK SATIR: Satın alınan yazılımları çekme
    satın_alinan_yazilimlar = Purchase.objects.filter(user=request.user, paid=True).select_related('product')


    return render(request, "profil.html", {
        "user": request.user,
        "kullanici_egitimleri": satin_almalar,
        "satın_alinan_kitaplar": satın_alinan_kitaplar,
        "satın_alinan_oyunlar": satın_alinan_oyunlar,
        "satın_alinan_yazilimlar": satın_alinan_yazilimlar, # Yazılımları da template'e gönderiyoruz
    })

@login_required(login_url='/kullanici/giris/')
def profil_duzenle(request):
    if request.method == 'POST':
        try:
            kullanici_adi = request.POST.get('kullanici_adi', '').strip()
            email = request.POST.get('email', '').strip()
            yeni_sifre = request.POST.get('sifre', '').strip()

            if kullanici_adi and kullanici_adi != request.user.username:
                if User.objects.exclude(pk=request.user.pk).filter(username=kullanici_adi).exists():
                    return render(request, 'kullanici/profil_duzenle.html', {
                        'hata': 'Bu kullanıcı adı zaten alınmış.',
                        'kullanici': request.user
                    })
                request.user.username = kullanici_adi

            if email:
                request.user.email = email

            if yeni_sifre:
                request.user.set_password(yeni_sifre)
                request.user.save()
                update_session_auth_hash(request, request.user)  # oturumu açık tutar
                return redirect('/')
            else:
                request.user.save()
                return redirect('/')

        except MultiValueDictKeyError:
            return render(request, 'kullanici/profil_duzenle.html', {
                'hata': 'Form eksik gönderildi.',
                'kullanici': request.user
            })

    return render(request, 'kullanici/profil_duzenle.html', {'kullanici': request.user})



@login_required(login_url='/kullanici/giris/')
def sifre_degistir(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('/')
        else:
            return render(request, 'kullanici/sifre_degistir.html', {'form': form, 'hata': 'Lütfen geçerli bilgiler giriniz.'})
    else:
        form = PasswordChangeForm(user=request.user)
        return render(request, 'kullanici/sifre_degistir.html', {'form': form})