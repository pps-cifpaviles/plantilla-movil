"""Tests de las partes que no dependen de la interfaz gráfica."""
from oxygenmovil import crypto
from oxygenmovil.storage import Almacen


def test_cifrar_y_descifrar():
    assert crypto.descifrar(crypto.cifrar("token-de-prueba")) == "token-de-prueba"


def test_sesion_se_guarda_y_se_borra(tmp_path):
    almacen = Almacen(tmp_path)
    almacen.guardar_sesion("ana", "secreto", "tok", "u1")
    assert almacen.leer_sesion()["token"] == "tok"
    almacen.borrar_sesion()
    assert almacen.leer_sesion() is None


def test_huella():
    # Importación diferida: app.py importa toga, que no está en todos los entornos de test
    import importlib.util
    if importlib.util.find_spec("toga") is None:
        return
    from oxygenmovil.app import huella
    acts = [{"distancia": 10, "tipo_transporte": "Coche"}, {"distancia": 5, "tipo_transporte": "Tren"}]
    assert huella(acts, {"Coche": 1.5, "Tren": 0.1}) == 15.5
