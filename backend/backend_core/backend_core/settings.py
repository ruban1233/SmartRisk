import os
from pathlib import Path
from dotenv import load_dotenv

# =====================================
# BASE DIRECTORY
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# =====================================
# LOAD ENV
# =====================================

dotenv_path = BASE_DIR / ".env"

if dotenv_path.exists():
    load_dotenv(dotenv_path)
    print("✅ .env loaded:", dotenv_path)
else:
    print("⚠ .env not found")


# =====================================
# SECURITY
# =====================================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "smart-risk-dev-key")

DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]


# =====================================
# INSTALLED APPS
# =====================================

INSTALLED_APPS = [

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "corsheaders",
    "rest_framework",

    "coreapi",
]


# =====================================
# MIDDLEWARE
# =====================================

MIDDLEWARE = [

    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =====================================
# CORS SETTINGS
# =====================================

CORS_ALLOW_ALL_ORIGINS = True


# =====================================
# URL CONFIG
# =====================================

ROOT_URLCONF = "backend_core.urls"


# =====================================
# TEMPLATES
# =====================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [

                "django.template.context_processors.debug",
                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

            ],
        },
    },
]


# =====================================
# WSGI
# =====================================

WSGI_APPLICATION = "backend_core.wsgi.application"


# =====================================
# DATABASE
# =====================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",

        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# =====================================
# PASSWORD VALIDATORS
# =====================================

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },

    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },

]


# =====================================
# LANGUAGE
# =====================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# =====================================
# STATIC FILES
# =====================================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# =====================================
# DEFAULT FIELD
# =====================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# =====================================
# REST FRAMEWORK
# =====================================

REST_FRAMEWORK = {

    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ]
}


# =====================================
# ANGEL API
# =====================================

ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")

ANGEL_CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")

ANGEL_MPIN = os.getenv("ANGEL_MPIN")

ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")


# =====================================
# LOGGING (Reduce Broken Pipe Logs)
# =====================================

LOGGING = {

    "version": 1,

    "disable_existing_loggers": False,

    "handlers": {

        "console": {
            "class": "logging.StreamHandler",
        },

    },

    "loggers": {

        "django.server": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },

    },

}