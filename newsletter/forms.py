# newsletter/forms.py
from django import forms
from .models import Subscriber

class SubscriberForm(forms.ModelForm):
    # HTML'deki radyo düğmeleri için de choices tanımlaması yapabiliriz
    user_type = forms.ChoiceField(
        choices=Subscriber.USER_TYPE_CHOICES,
        widget=forms.RadioSelect, # Radyo düğmesi olarak render edilmesini sağlar
        initial='ogrenci', # Varsayılan seçim
        label="Kullanıcı Tipi"
    )

    class Meta:
        model = Subscriber
        fields = ['email', 'user_type'] # Modeldeki hangi alanları formda kullanacağımızı belirtiyoruz
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'E-posta Adresiniz'}),
        }