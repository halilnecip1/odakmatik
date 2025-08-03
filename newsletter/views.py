# newsletter/views.py (Form ile)
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SubscriberForm
from .models import Subscriber

def subscribe_newsletter(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user_type = form.cleaned_data['user_type']
            
            try:
                # Mevcut abone mi kontrol et
                subscriber, created = Subscriber.objects.get_or_create(
                    email=email,
                    defaults={'user_type': user_type}
                )
                if not created:
                    if subscriber.user_type != user_type:
                        subscriber.user_type = user_type
                        subscriber.save()
                        messages.info(request, "E-posta adresiniz zaten bültenimize kayıtlıydı. Kullanıcı tipiniz güncellendi.")
                    else:
                        messages.info(request, "E-posta adresiniz zaten bültenimize kayıtlı.")
                else:
                    messages.success(request, "Bültenimize başarıyla abone oldunuz! Teşekkür ederiz.")
                
            except Exception as e:
                messages.error(request, f"Abone olurken bir hata oluştu: {e}")
                print(f"Bülten abonelik hatası: {e}")
        else:
            # Form geçerli değilse hata mesajlarını göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")

        return redirect('index')
    return redirect('index')