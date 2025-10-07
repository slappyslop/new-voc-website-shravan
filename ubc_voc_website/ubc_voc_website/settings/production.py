from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("DATABASE_HOST", "db"),
        "PORT": "5432"
    }
}

ROOT_URLCONF = 'ubc_voc_website.urls'

# TODO replace this with SES once that's set up
# Outputs all emails to the console, so we don't need a separate SMTP server in dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/home/ubc_voc_website/staticfiles'

CSRF_TRUSTED_ORIGINS = [
    f"http://{host}:8082" for host in ALLOWED_HOSTS
] + [
    f"https://{host}:8082" for host in ALLOWED_HOSTS
]
