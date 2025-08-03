# instructor/forms.py
from django import forms
from django.contrib.auth import get_user_model

# Modelleri import edin (HEPSİ instructor/models.py içinde olduğu varsayımıyla)
from .models import (
    Profile, InstructorStudent, Course, LiveLesson, # Mevcut modeller
    
)

User = get_user_model()


class AssignCourseForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=User.objects.none(), # Queryset view'de ayarlanacak
        label="Öğrenci Seç",
        widget=forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), # Tüm kursları listeliyoruz
        label="Atanacak Kursu Seç",
        widget=forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )

class EgitmenOgrenciEkleForm(forms.Form):
    ogrenci = forms.ModelChoiceField(queryset=User.objects.none(), label="Öğrenci Seçin")
    DURATION_CHOICES = [(i, f"{i} Ay") for i in range(1, 13)]
    duration_months = forms.ChoiceField(
        choices=DURATION_CHOICES, 
        label="Abonelik Süresi",
        required=True,
        help_text="Öğrencinin eğitmenle olan abonelik süresini seçin."
    )

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, label="Adınız")
    last_name = forms.CharField(max_length=150, required=False, label="Soyadınız")

    class Meta:
        model = Profile
        fields = ['profile_picture']
        labels = {
            'profile_picture': 'Profil Fotoğrafı',
        }
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'hidden', 'id': 'profile_picture_input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'profile_picture':
                pass
            else:
                field.widget.attrs.update({'class': 'w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500'})
        
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        
        user.first_name = self.cleaned_data.get('first_name', user.first_name)
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        user.save()

        if hasattr(profile, 'first_name') and self.cleaned_data.get('first_name'):
            profile.first_name = self.cleaned_data['first_name']
        if hasattr(profile, 'last_name') and self.cleaned_data.get('last_name'):
            profile.last_name = self.cleaned_data['last_name']
        
        if commit:
            profile.save()
        return profile
    
class LiveLessonForm(forms.ModelForm):
    class Meta:
        model = LiveLesson
        fields = ['title', 'meeting_url', 'start_time']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dersin Başlığı (örn: Okuma Hızı Teknikleri)'}),
            'meeting_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://zoom.us/j/...'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        labels = {
            'title': 'Ders Başlığı',
            'meeting_url': 'Toplantı Linki (Zoom, Meet vb.)',
            'start_time': 'Ders Tarihi ve Saati',
        } 

