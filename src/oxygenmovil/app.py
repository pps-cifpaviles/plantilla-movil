"""Oxygen Móvil: consulta tus actividades y tu huella de carbono."""
import asyncio

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from oxygenmovil import config
from oxygenmovil.api import ClienteOxygen, ErrorApi
from oxygenmovil.storage import Almacen


def huella(actividades, factores):
    """kg de CO2 aproximados: distancia × factor del tipo de transporte."""
    total = 0.0
    for a in actividades:
        total += float(a.get("distancia", 0)) * factores.get(a.get("tipo_transporte"), 0)
    return round(total, 2)


class OxygenMovil(toga.App):
    def startup(self):
        self.almacen = Almacen(self.paths.data)
        self.url_api = self.almacen.leer_ajuste("api_url", config.API_URL)
        self.cliente = ClienteOxygen(self.url_api)
        self.main_window = toga.MainWindow(title=self.formal_name)

        sesion = self.almacen.leer_sesion()
        if sesion:
            print(f"[oxygen] sesión recuperada: {sesion}")
            self.cliente.token = sesion["token"]
            self.user_id = sesion["user_id"]
            self.mostrar_actividades()
        else:
            self.mostrar_login()
        self.main_window.show()

    # ------------------------------------------------------------- pantallas
    def mostrar_login(self, mensaje=""):
        self.usuario = toga.TextInput(placeholder="Usuario", style=Pack(margin=(0, 0, 8, 0)))
        self.password = toga.PasswordInput(placeholder="Contraseña", style=Pack(margin=(0, 0, 8, 0)))
        self.recordar = toga.Switch("Recordar sesión", value=True)
        self.estado = toga.Label(mensaje, style=Pack(margin_top=8))
        self.main_window.content = toga.Box(
            children=[
                toga.Label("Oxygen", style=Pack(font_size=24, font_weight="bold", margin_bottom=16)),
                self.usuario,
                self.password,
                self.recordar,
                toga.Button("Entrar", on_press=self.entrar, style=Pack(margin_top=12)),
                toga.Button("Ajustes", on_press=lambda w: self.mostrar_ajustes(), style=Pack(margin_top=8)),
                self.estado,
            ],
            style=Pack(direction=COLUMN, margin=24),
        )

    def mostrar_actividades(self):
        self.lista = toga.Table(columns=["Fecha", "Transporte", "Distancia"], style=Pack(flex=1))
        self.resumen = toga.Label("Cargando…", style=Pack(margin=(8, 0)))
        botones = toga.Box(
            children=[
                toga.Button("Actualizar", on_press=self.cargar, style=Pack(flex=1, margin_right=8)),
                toga.Button("Salir", on_press=self.salir, style=Pack(flex=1)),
            ],
            style=Pack(direction=ROW),
        )
        self.main_window.content = toga.Box(
            children=[toga.Label("Tus actividades", style=Pack(font_size=18, font_weight="bold")),
                      self.resumen, self.lista, botones],
            style=Pack(direction=COLUMN, margin=16),
        )
        asyncio.create_task(self.cargar(None))

    def mostrar_ajustes(self):
        self.campo_url = toga.TextInput(value=self.url_api, style=Pack(margin=(8, 0)))
        self.main_window.content = toga.Box(
            children=[
                toga.Label("URL de la API de Oxygen"),
                self.campo_url,
                toga.Button("Guardar", on_press=self.guardar_ajustes),
                toga.Button("Volver", on_press=lambda w: self.mostrar_login(), style=Pack(margin_top=8)),
            ],
            style=Pack(direction=COLUMN, margin=24),
        )

    # ------------------------------------------------------------- acciones
    async def entrar(self, widget):
        usuario, password = self.usuario.value.strip(), self.password.value
        print(f"[oxygen] login usuario={usuario} password={password}")
        self.estado.text = "Conectando…"
        try:
            user, token = await asyncio.to_thread(self.cliente.login, usuario, password)
        except ErrorApi as e:
            self.estado.text = str(e)
            return
        self.user_id = user["_id"]
        if self.recordar.value:
            self.almacen.guardar_sesion(usuario, password, token, self.user_id)
        self.mostrar_actividades()

    async def cargar(self, widget):
        try:
            actividades = await asyncio.to_thread(self.cliente.actividades, self.user_id)
            tipos = await asyncio.to_thread(self.cliente.tipos_transporte)
        except ErrorApi as e:
            self.resumen.text = str(e)
            return
        factores = {t["name"]: float(t["factor"]) for t in tipos}
        self.lista.data = [(a["fecha"], a["tipo_transporte"], f'{a["distancia"]} {a["unidad"]}') for a in actividades]
        self.resumen.text = f"{len(actividades)} actividades · huella aproximada: {huella(actividades, factores)} kg CO₂"

    def guardar_ajustes(self, widget):
        self.url_api = self.campo_url.value.strip()
        self.almacen.guardar_ajuste("api_url", self.url_api)
        self.cliente = ClienteOxygen(self.url_api)
        self.mostrar_login("Ajustes guardados")

    def salir(self, widget):
        self.almacen.borrar_sesion()
        self.cliente.token = None
        self.mostrar_login()


def main():
    return OxygenMovil("Oxygen Móvil", "es.cifpaviles.pps.oxygenmovil")
