from .base import *
import dj_database_url

INSTALLED_APPS += ['core_app', 'crispy_forms', 'delta_rn']

# ==============================================================================
# EMAIL SETTINGS
# ==============================================================================

EMAIL_HOST = config("EMAIL_HOST")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# ==============================================================================
# DATABASES SETTINGS
# ==============================================================================

DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default="postgres://simple:simple@localhost:5432/simple"),
        conn_max_age=600,
    )
}

