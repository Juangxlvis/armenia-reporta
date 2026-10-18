import pytest
from django.core.files.storage import default_storage, storages
from django.utils.functional import empty

STORAGES_LOCAL = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {},
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


@pytest.fixture(autouse=True)
def storage_local(settings, tmp_path):
    settings.STORAGES = STORAGES_LOCAL
    settings.MEDIA_ROOT = str(tmp_path)
    settings.MEDIA_URL = "/media/"

    storages._storages.clear()
    storages.__dict__.pop("backends", None)
    default_storage._wrapped = empty

    yield

    storages._storages.clear()
    storages.__dict__.pop("backends", None)
    default_storage._wrapped = empty
