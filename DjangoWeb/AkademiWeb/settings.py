import os
import pyrebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '#8+fvin=@4mxgjibq8hc=wcl5g3dvgi^kt!4ch(9sb@4qnjcl^r$kf_'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'AkademiApp',
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

firebaseConfig = {
  "apiKey": "",
  "authDomain": "",
  "databaseURL": "",
  "projectId": "",
  "storageBucket": "",
  "messagingSenderId": "",
  "appId": "",
  "measurementId": ""
}

"""firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
cred = credentials.Certificate('firebase-adminsdk.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
db_storage = firebase.storage()"""
ROOT_URLCONF = 'AkademiWeb.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR+'/templates/'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries':{
                    'template_filters': 'AkademiApp.template_filters',
                }

        },
    },
]

WSGI_APPLICATION = 'AkademiWeb.wsgi.application'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')