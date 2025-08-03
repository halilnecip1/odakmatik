#benim_sitem settings.py

from pathlib import Path
import os 
from dotenv import load_dotenv

load_dotenv()
import dj_database_url
LOGIN_URL = '/kullanici/kayit/'  # senin giriş yaptığın URL neyse onu yaz


BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = 'django-insecure-w%kx756c8$^v2g%p6l9=yjlq1ea46hp8jbn)ogkvp$ygt*p+1a'

#STRIPE_WEBHOOK_SECRET = 'whsec_e5183ded486a388f8f90f768e16f97e0b76f2dde1fa581a2abb82e62ded7c89f'

DEBUG = False

ALLOWED_HOSTS = ['odakmatik-env-v2.eba-vsch2ygp.eu-central-1.elasticbeanstalk.com',
                 '3.121.41.76',
    'localhost',
    '127.0.0.1',
    '192.168.1.134',]



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'widget_tweaks',
    'anasayfa',
    'kullanici',
    'egitimler',
    'satinalim',
    'ilerleme',
    'shop',
    'instructor',
    'student',
    'newsletter',
    'exercises',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'benim_sitem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # ← BU SATIR OLMALI
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'benim_sitem.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_database', # <-- Buraya Django projenizin kullanacağı DB adını yazın
        'USER': 'django_user',    # <-- Buraya Django için oluşturacağınız MySQL kullanıcı adını yazın
        'PASSWORD': 'MyS3cret_P@ssw0rd!', # <-- Buraya o kullanıcının şifresini yazın
        'HOST': '127.0.0.1',      # MySQL aynı sunucuda olduğu için localhost'u kullanın
        'PORT': '3306',           # MySQL'in varsayılan portu
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}



AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')




DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

#STRIPE_PUBLIC_KEY = 'pk_test_51RSfWqCiXnvhF6rqi2fyGQGm8Jm0K8m8WWUSbyCCTiXguIDHRyf6Lbi4sAqDeLg5R3G5NAxbbkp1uq4cTYmXvc5000AJuNTpGg'
#STRIPE_SECRET_KEY = 'sk_test_51RSfWqCiXnvhF6rqLjIHXSg9S1pnDE51Xidu3PKsmRgwzatxxqDjNVwLl0MLuxt3w3oAbw6Y8p5f1OPXlvhNjAaK00Fb9xI8Ff'
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') # <-- BU SATIRI EKLEYİN

# Diğer Stripe anahtarları (varsa ve .env'den alınıyorsa)
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY') # <-- Bu da .env'den alınmalı
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')


# E-POSTA AYARLARI (OUTLOOK.COM / HOTMAIL / LIVE.COM İÇİN)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'  # Outlook/Office 365 için SMTP sunucusu
# veya bazen 'smtp.live.com' veya 'smtp-mail.outlook.com' da olabilir
EMAIL_PORT = 587
EMAIL_USE_TLS = True         # TLS şifrelemesi kullanılsın mı?
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER') # <-- YENİ EKLENDİ
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD') 

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL') # <-- YENİ EKLENDİ
SERVER_EMAIL = os.environ.get('SERVER_EMAIL') # <-- YENİ EKLENDİ
