from pathlib import Path
from decouple import config, Csv
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY',
             default='django-insecure-getbua-secret-key-change-me')
DEBUG      = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS',
                default='127.0.0.1,localhost', cast=Csv())

CSRF_TRUSTED_ORIGINS = [
    'https://web-production-8c0589.up.railway.app',
    'http://web-production-8c0589.up.railway.app',
]

INSTALLED_APPS = [
    # Jazzmin MUST be first before django.contrib.admin
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

# ─── JAZZMIN SETTINGS ─────────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    "site_title":        "GetBua Admin",
    "site_header":       "GetBua",
    "site_brand":        "🏠 GetBua",
    "site_logo":         None,
    "welcome_sign":      "Welcome to GetBua Admin Panel",
    "copyright":         "GetBua 2026",
    "search_model":      ["auth.User", "core.Worker"],
    "topmenu_links": [
        {"name": "Home",      "url": "admin:index"},
        {"name": "Workers",   "model": "core.Worker"},
        {"name": "Hires",     "model": "core.HiringRequest"},
        {"name": "Messages",  "model": "core.Message"},
        {"name": "Live Site", "url": "/", "new_window": True},
    ],
    "usermenu_links": [
        {"name": "Live Site", "url": "/", "new_window": True},
        {"model": "auth.user"}
    ],
    "show_sidebar":             True,
    "navigation_expanded":      True,
    "hide_apps":                [],
    "hide_models":              [],
    "order_with_respect_to":    [
        "core", "auth",
        "core.Worker", "core.HiringRequest", "core.Contract",
        "core.Review", "core.ReplacementRequest",
        "core.Message", "core.SalaryPayment", "core.UserProfile",
    ],
    "icons": {
        "auth":                     "fas fa-users-cog",
        "auth.user":                "fas fa-user",
        "auth.Group":               "fas fa-users",
        "core.Worker":              "fas fa-hard-hat",
        "core.HiringRequest":       "fas fa-briefcase",
        "core.Contract":            "fas fa-file-contract",
        "core.Review":              "fas fa-star",
        "core.ReplacementRequest":  "fas fa-exchange-alt",
        "core.Message":             "fas fa-envelope",
        "core.SalaryPayment":       "fas fa-money-bill-wave",
        "core.UserProfile":         "fas fa-id-card",
    },
    "default_icon_parents":  "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active":  True,
    "custom_css":            None,
    "custom_js":             None,
    "use_google_fonts_cdn":  True,
    "show_ui_builder":       False,
    "changeform_format":     "horizontal_tabs",
    "language_chooser":      False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text":    False,
    "footer_small_text":    False,
    "body_small_text":      False,
    "brand_small_text":     False,
    "brand_colour":         "navbar-primary",
    "accent":               "accent-primary",
    "navbar":               "navbar-white navbar-light",
    "no_navbar_border":     False,
    "navbar_fixed":         True,
    "layout_boxed":         False,
    "footer_fixed":         False,
    "sidebar_fixed":        True,
    "sidebar":              "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme":                "default",
    "dark_mode_theme":      None,
    "button_classes": {
        "primary":  "btn-primary",
        "secondary":"btn-secondary",
        "info":     "btn-info",
        "warning":  "btn-warning",
        "danger":   "btn-danger",
        "success":  "btn-success",
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'getbua.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'getbua.wsgi.application'

DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME':   BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE     = 'Asia/Dhaka'
USE_I18N      = True
USE_TZ        = True

STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = config('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = 'GetBua <noreply@getbua.com>'

DEFAULT_AUTO_FIELD  = 'django.db.models.BigAutoField'
LOGIN_URL           = '/login/'
LOGIN_REDIRECT_URL  = '/'
LOGOUT_REDIRECT_URL = '/'