from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def _strip_mysql_ssl_query_params(url: str) -> str:
    """mysqlclient rejects ssl-mode in the URL; SSL is set via OPTIONS instead."""
    if not url or "?" not in url:
        return url
    parsed = urlparse(url)
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in {"ssl-mode", "ssl_mode"}
    ]
    return urlunparse(parsed._replace(query=urlencode(query)))


_DEV_SECRET = "dev-only-change-in-production"
SECRET_KEY = config("SECRET_KEY", default=_DEV_SECRET)
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1,testserver", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "catalog",
    "cart",
    "orders",
    "shop",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

_TEMPLATE_CONTEXT_PROCESSORS = [
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "shop.context_processors.cart_summary",
]
if DEBUG:
    _TEMPLATE_CONTEXT_PROCESSORS.insert(1, "django.template.context_processors.debug")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": _TEMPLATE_CONTEXT_PROCESSORS,
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASE_URL = config("DATABASE_URL", default="")
USE_SQLITE = config("USE_SQLITE", default=False, cast=bool)

if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(_strip_mysql_ssl_query_params(DATABASE_URL))}
    _parsed_opts = DATABASES["default"].get("OPTIONS", {})
    for _bad_key in ("ssl-mode", "ssl_mode"):
        _parsed_opts.pop(_bad_key, None)
else:
    DATABASES = {
        "default": {
            "ENGINE": config("DB_ENGINE", default="django.db.backends.mysql"),
            "NAME": config("DB_NAME", default="ecommerce_db"),
            "USER": config("DB_USER", default="root"),
            "PASSWORD": config("DB_PASSWORD", default=""),
            "HOST": config("DB_HOST", default="127.0.0.1"),
            "PORT": config("DB_PORT", default="3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

if DEBUG:
    STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

if not DEBUG:
    if SECRET_KEY == _DEV_SECRET:
        raise ImproperlyConfigured("Set a unique SECRET_KEY environment variable for production.")
    if not ALLOWED_HOSTS or set(ALLOWED_HOSTS) <= {"localhost", "127.0.0.1", "testserver"}:
        raise ImproperlyConfigured("Set ALLOWED_HOSTS to your production domain(s).")
    if not CSRF_TRUSTED_ORIGINS:
        raise ImproperlyConfigured("Set CSRF_TRUSTED_ORIGINS (e.g. https://your-app.onrender.com).")
    if USE_SQLITE:
        raise ImproperlyConfigured("USE_SQLITE must be False in production.")

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"

if not USE_SQLITE and DATABASES.get("default"):
    DATABASES["default"].setdefault("CONN_MAX_AGE", 60)
    _engine = DATABASES["default"].get("ENGINE", "")
    if "mysql" in _engine:
        _opts = DATABASES["default"].setdefault("OPTIONS", {})
        _opts.setdefault("charset", "utf8mb4")
        _opts.setdefault("init_command", "SET sql_mode='STRICT_TRANS_TABLES'")
        _ssl_ca = config("MYSQL_SSL_CA", default="")
        _needs_ssl = (
            bool(_ssl_ca)
            or config("MYSQL_SSL_REQUIRED", default=False, cast=bool)
            or "aivencloud.com" in DATABASE_URL
            or "ssl-mode=required" in DATABASE_URL.lower()
        )
        if _needs_ssl:
            _opts.setdefault("ssl", {"ca": _ssl_ca} if _ssl_ca else {})

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO" if not DEBUG else "DEBUG",
    },
}
