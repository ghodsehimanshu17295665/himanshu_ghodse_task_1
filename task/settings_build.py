from .settings import *

# Disable database usage during build
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy'
    }
}
