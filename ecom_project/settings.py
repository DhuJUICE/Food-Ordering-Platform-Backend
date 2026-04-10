from pathlib import Path
import os 
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

IMAGEKIT_PRIVATE_KEY = config('IMAGEKIT_PRIVATE_KEY')

PAYFAST_TEST_MERCHANT_ID = config('PAYFAST_TEST_MERCHANT_ID')
PAYFAST_TEST_MERCHANT_KEY = config('PAYFAST_TEST_MERCHANT_KEY')

PAYFAST_LIVE_MERCHANT_ID = config('PAYFAST_LIVE_MERCHANT_ID')
PAYFAST_LIVE_MERCHANT_KEY = config('PAYFAST_LIVE_MERCHANT_KEY')

SECRET_KEY = config('SECRET_KEY')

#Authentication access-token and refresh-token lifetimes
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

IN_PRODUCTION = config('IN_PRODUCTION', cast=bool)

# SECURITY WARNING: don't run with debug turned on in production!
if IN_PRODUCTION == True:
    DEBUG = False
else:
    DEBUG = True

# -------------------------
# SESSION CONFIGURATION
# -------------------------
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True

if IN_PRODUCTION == True:
    SESSION_COOKIE_SAMESITE = 'None'  # or 'None' if frontend is separate
    SESSION_COOKIE_SECURE = True # True in production (HTTPS)
else:
    SESSION_COOKIE_SAMESITE = 'Lax'   # or 'None' if frontend is separate
    SESSION_COOKIE_SECURE = False 

#Allowed hosts is what deployed hosts that can communicate with this application
ALLOWED_HOSTS = [
    'heranbites-backend.onrender.com',
    '127.0.0.1',
    'localhost',
    'jewelry-graphics-overcome-achieving.trycloudflare.com'
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'user_management',
    'product_management',
    'cart_management',
    'checkout_management',

    'order_management',

    'tenant_management',

    'auth_management',

    'api_management',

    'rest_framework',
    'corsheaders',
    
    #for api documentation
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:3000',
    'http://localhost:3000',
    'https://heranbites.onrender.com', #deployed fronted
]

#do not use cors_allow_all_origins when using credentials=True from frontend
#CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    'https://heranbites.onrender.com', #deployed fronted
]

CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'ecom_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'api_management/html_templates',
        ],
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

WSGI_APPLICATION = 'ecom_project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Keep this hardcoded
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
        'OPTIONS': {
            'sslmode': config('DB_SSLMODE', default='require'),
        },
    }
}

# Password validation
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

#AUTHENTICATION MECHANISMS
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'auth_management.authentication.CookieJWTAuthentication',
        #'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
