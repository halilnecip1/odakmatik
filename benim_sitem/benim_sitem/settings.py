#benim_sitem settings.py

from pathlib import Path
import os 

LOGIN_URL = '/kullanici/kayit/'  # senin giriş yaptığın URL neyse onu yaz


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w%kx756c8$^v2g%p6l9=yjlq1ea46hp8jbn)ogkvp$ygt*p+1a'

STRIPE_WEBHOOK_SECRET = 'whsec_e5183ded486a388f8f90f768e16f97e0b76f2dde1fa581a2abb82e62ded7c89f'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

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


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STRIPE_PUBLIC_KEY = 'pk_test_51RSfWqCiXnvhF6rqi2fyGQGm8Jm0K8m8WWUSbyCCTiXguIDHRyf6Lbi4sAqDeLg5R3G5NAxbbkp1uq4cTYmXvc5000AJuNTpGg'
#STRIPE_SECRET_KEY = 'sk_test_51RSfWqCiXnvhF6rqLjIHXSg9S1pnDE51Xidu3PKsmRgwzatxxqDjNVwLl0MLuxt3w3oAbw6Y8p5f1OPXlvhNjAaK00Fb9xI8Ff'



# E-POSTA AYARLARI (OUTLOOK.COM / HOTMAIL / LIVE.COM İÇİN)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.office365.com'  # Outlook/Office 365 için SMTP sunucusu
# veya bazen 'smtp.live.com' veya 'smtp-mail.outlook.com' da olabilir
EMAIL_PORT = 587
EMAIL_USE_TLS = True         # TLS şifrelemesi kullanılsın mı?
EMAIL_HOST_USER = 'h@outlook.com' # Kendi Outlook/Hotmail/Live adresiniz
EMAIL_HOST_PASSWORD = 'h' # Outlook hesabınızın şifresi

# İletişim formu mesajlarının gönderileceği e-posta adresi (giden)
DEFAULT_FROM_EMAIL = 'h@outlook.com' # Genellikle EMAIL_HOST_USER ile aynı olabilir
SERVER_EMAIL = 'h@outlook.com' # Hata mesajları vs. için kullanılan email
