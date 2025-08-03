
# satinalim/views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from egitimler.models import Egitim
from .models import SatinAlim
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import SatinAlim, Egitim
from django.contrib.auth.models import User
import json
from django.views.decorators.http import require_POST

stripe.api_key = settings.STRIPE_SECRET_KEY

STRIPE_WEBHOOK_SECRET = 'whsec_e5183ded486a388f8f90f768e16f97e0b76f2dde1fa581a2abb82e62ded7c89f'


@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    # Etkinlik tipi kontrolü
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Session metadata'dan kullanıcı ve eğitim ID'lerini alacağız
        customer_email = session.get('customer_email')
        egitim_id = session.get('metadata', {}).get('egitim_id')

        if customer_email and egitim_id:
            try:
                user = User.objects.get(email=customer_email)
                egitim = Egitim.objects.get(id=egitim_id)
                # Kullanıcıya eğitimi tanımla
                SatinAlim.objects.get_or_create(user=user, egitim=egitim)
            except User.DoesNotExist:
                pass
            except Egitim.DoesNotExist:
                pass

    return HttpResponse(status=200)



@login_required
def satin_al(request, egitim_id):
    egitim = get_object_or_404(Egitim, id=egitim_id)

    # Kullanıcı daha önce bu eğitimi satın aldıysa tekrar alma
    satin_alindi_mi = SatinAlim.objects.filter(kullanici=request.user, egitim=egitim).exists()
    if satin_alindi_mi:
        return redirect('egitim_detay', egitim_id=egitim.id)

    # Satın alma işlemi
    SatinAlim.objects.create(kullanici=request.user, egitim=egitim)
    return redirect('egitim_detay', egitim_id=egitim.id)
