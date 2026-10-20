# Oxygen Móvil — plantilla del curso

Oxygen Móvil es una app Android escrita en **Python** con [BeeWare](https://beeware.org): la interfaz usa Toga y el APK se genera con Briefcase. Es un cliente de la API de [Oxygen](https://github.com/pps-cifpaviles/plantilla-oxygen): inicia sesión, muestra tus actividades y calcula una huella de carbono aproximada.

> ⚠️ **App vulnerable a propósito.** Contiene fallos de seguridad sembrados para el bloque de aplicaciones móviles (OWASP MASVS y MASTG). Tu trabajo es encontrarlos con análisis estático y dinámico, documentarlos y corregirlos.

## Crea tu copia

```bash
gh repo create pps-cifpaviles/a07-movil --template pps-cifpaviles/plantilla-movil --public --clone
cd a07-movil
git switch develop
```

## Estructura

| Fichero | Contenido |
| --- | --- |
| `src/oxygenmovil/app.py` | Interfaz: login, lista de actividades y ajustes |
| `src/oxygenmovil/api.py` | Cliente HTTP de la API de Oxygen (solo biblioteca estándar) |
| `src/oxygenmovil/storage.py` | Sesión y ajustes guardados en SQLite |
| `src/oxygenmovil/crypto.py` | «Cifrado» de datos locales |
| `src/oxygenmovil/config.py` | URL de la API y otras opciones |
| `pyproject.toml` | Configuración de Briefcase, incluido el manifiesto de Android |
| `tests/` | Tests de las partes sin interfaz |

## Ejecutarla en tu equipo

En modo desarrollo, como app de escritorio (Linux, Windows o macOS):

```bash
python -m venv .venv && source .venv/bin/activate
pip install briefcase==0.4.6
briefcase dev
```

Para Android, Briefcase descarga por sí mismo el JDK y el SDK la primera vez (varios GB):

```bash
briefcase create android
briefcase build android
briefcase run android                      # lanza un emulador o usa el móvil conectado
briefcase package android -p debug-apk     # APK en dist/
```

O descarga el APK que genera el pipeline, en la pestaña *Actions → artefacto `apk`*, e instálalo con `adb install oxygenmovil-debug.apk`.

## Configurar la URL de la API

La app apunta por defecto a `http://pps-dev.aula.lan:20711/api`. Cámbiala en `config.py` o desde la pantalla de **Ajustes** al puerto de tu API (`20000 + NN×100 + 11`). Desde el emulador de Android, tu equipo anfitrión es `10.0.2.2`.

## Pipeline

| Evento | Jobs |
| --- | --- |
| Pull request | `test` y `build-apk` (runners de GitHub) |
| Push a `develop` o tag `v*` | Además, `mobsf`: análisis estático en el MobSF del aula (runner `pps-dev`) |

El job `mobsf` necesita el secreto `MOBSF_API_KEY`, que proporciona el profesorado.

## Cómo se ejecuta Python en Android

Al abrir el APK con `jadx` verás sobre todo código Java: es el *bootstrap* que arranca un intérprete CPython embebido. Tu código Python va empaquetado aparte dentro del APK. Descubrir dónde está y cómo extraerlo forma parte del laboratorio.

## Colaboradores

<!-- Añade aquí tu nombre y tu usuario de GitHub. -->
