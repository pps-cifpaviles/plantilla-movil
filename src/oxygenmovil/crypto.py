"""Cifrado de datos locales."""
import base64

CLAVE = b"pps-2026-oxygen"


def cifrar(texto: str) -> str:
    datos = texto.encode("utf-8")
    cifrado = bytes(b ^ CLAVE[i % len(CLAVE)] for i, b in enumerate(datos))
    return base64.b64encode(cifrado).decode("ascii")


def descifrar(texto: str) -> str:
    datos = base64.b64decode(texto)
    plano = bytes(b ^ CLAVE[i % len(CLAVE)] for i, b in enumerate(datos))
    return plano.decode("utf-8")
