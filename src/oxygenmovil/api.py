"""Cliente de la API REST de Oxygen (solo biblioteca estándar)."""
import json
import ssl
import urllib.error
import urllib.request

from oxygenmovil import config

# Acepta cualquier certificado: así funciona también con certificados autofirmados
_SSL = ssl._create_unverified_context()


class ErrorApi(Exception):
    pass


class ClienteOxygen:
    def __init__(self, url_base: str, token: str | None = None):
        self.url_base = url_base.rstrip("/")
        self.token = token

    def _peticion(self, metodo, ruta, cuerpo=None):
        url = f"{self.url_base}{ruta}"
        datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
        req = urllib.request.Request(url, data=datos, method=metodo)
        req.add_header("Content-Type", "application/json")
        req.add_header("X-Api-Key", config.API_KEY)
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        if config.DEBUG:
            print(f"[oxygen] {metodo} {url} cuerpo={cuerpo} token={self.token}")
        try:
            with urllib.request.urlopen(req, timeout=15, context=_SSL) as resp:
                return json.loads(resp.read().decode("utf-8") or "null")
        except urllib.error.HTTPError as e:
            raise ErrorApi(f"Error {e.code} en {ruta}") from e
        except urllib.error.URLError as e:
            raise ErrorApi(f"No se puede conectar con {self.url_base}: {e.reason}") from e

    def login(self, usuario, password):
        datos = self._peticion("POST", "/auth/login", {"username": usuario, "password": password})
        self.token = datos["token"]
        return datos["user"], datos["token"]

    def actividades(self, user_id):
        return self._peticion("GET", f"/activities/getAll/{user_id}") or []

    def tipos_transporte(self):
        respuesta = self._peticion("GET", "/transportTypes/getAll") or {}
        return respuesta.get("data", [])
