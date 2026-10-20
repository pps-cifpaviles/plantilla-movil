"""Almacenamiento local de la sesión y los ajustes (SQLite)."""
import sqlite3
from pathlib import Path

from oxygenmovil import crypto


class Almacen:
    def __init__(self, carpeta: Path):
        carpeta.mkdir(parents=True, exist_ok=True)
        self.ruta = carpeta / "oxygen.db"
        self.db = sqlite3.connect(self.ruta)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS sesion ("
            " id INTEGER PRIMARY KEY CHECK (id = 1),"
            " usuario TEXT, password TEXT, token TEXT, user_id TEXT)"
        )
        self.db.execute("CREATE TABLE IF NOT EXISTS ajustes (clave TEXT PRIMARY KEY, valor TEXT)")
        self.db.commit()

    # ---------------------------------------------------------------- sesión
    def guardar_sesion(self, usuario, password, token, user_id):
        self.db.execute(
            "INSERT OR REPLACE INTO sesion (id, usuario, password, token, user_id) VALUES (1, ?, ?, ?, ?)",
            (usuario, password, crypto.cifrar(token), user_id),
        )
        self.db.commit()

    def leer_sesion(self):
        fila = self.db.execute("SELECT usuario, password, token, user_id FROM sesion WHERE id = 1").fetchone()
        if not fila:
            return None
        usuario, password, token, user_id = fila
        return {"usuario": usuario, "password": password, "token": crypto.descifrar(token), "user_id": user_id}

    def borrar_sesion(self):
        self.db.execute("DELETE FROM sesion")
        self.db.commit()

    # --------------------------------------------------------------- ajustes
    def leer_ajuste(self, clave, por_defecto=None):
        fila = self.db.execute("SELECT valor FROM ajustes WHERE clave = ?", (clave,)).fetchone()
        return fila[0] if fila else por_defecto

    def guardar_ajuste(self, clave, valor):
        self.db.execute("INSERT OR REPLACE INTO ajustes (clave, valor) VALUES (?, ?)", (clave, valor))
        self.db.commit()
