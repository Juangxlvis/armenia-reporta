import uuid
from io import BytesIO

from django.core.exceptions import ValidationError
from PIL import Image

MAX_MB = 5
MAX_PIXELES = 1920
CALIDAD_JPEG = 85
FORMATOS_PERMITIDOS = {"JPEG", "PNG"}


def validar_foto(archivo):
    if archivo.size > MAX_MB * 1024 * 1024:
        raise ValidationError(f"Cada foto debe pesar máximo {MAX_MB} MB.")
    try:
        archivo.seek(0)
        with Image.open(archivo) as img:
            formato = (img.format or "").upper()
    except Exception as exc:
        raise ValidationError("El archivo no es una imagen válida.") from exc
    if formato not in FORMATOS_PERMITIDOS:
        raise ValidationError("Solo se permiten fotos JPG o PNG.")
    archivo.seek(0)


def comprimir_foto(archivo):
    archivo.seek(0)
    img = Image.open(archivo)
    img.load()
    formato = (img.format or "").upper()

    es_png_transparente = False
    if formato == "PNG" and (
        img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    ):
        es_png_transparente = True

    if max(img.size) > MAX_PIXELES:
        img.thumbnail((MAX_PIXELES, MAX_PIXELES), Image.Resampling.LANCZOS)

    salida = BytesIO()
    if es_png_transparente:
        img.save(salida, format="PNG", optimize=True)
        extension = ".png"
    else:
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.save(salida, format="JPEG", quality=CALIDAD_JPEG, optimize=True)
        extension = ".jpg"
    salida.seek(0)
    salida.name = f"{uuid.uuid4().hex}{extension}"
    return salida
