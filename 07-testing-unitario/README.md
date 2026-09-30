# 🧪 Módulo 07 — Testing Unitario (introducción)

> **Materia**: Desarrollo de Software 2026 · UTN FRLP
> **Tipo**: material complementario (no es entrega — formación de competencias)
> **Stack**: `uv` · Python 3.12 · FastAPI · `pytest`

---

## ¿De qué se trata?

Hasta acá escribiste código y lo verificaste **a mano**: corriste el server y
pegaste con curl (o corriste un script bash como `verificar_authz.sh`). Eso
funciona, pero no escala: cada cambio te obliga a re-verificar todo de nuevo,
y se te escapa lo que no pensaste en probar.

Este módulo te enseña a **automatizar esa verificación** con tests unitarios:
funciones que llaman a tu código y **fallan si cambió algo que no debía**.

> El test unitario es el seguro de vida de tu código. No te dice "está bien",
> te dice "sigue funcionando como cuando lo escribí". Y cuando algo se rompe,
> te dice **exactamente qué** y **dónde**.

---

## Qué vas a aprender

| Tema | Qué resuelve |
|------|--------------|
| **Test unitario** | Testear una función/clase aislada (sin DB, sin red) |
| **AAA** | Arrange / Act / Assert: la estructura de todo test |
| **Función pura** | Por qué es el caso ideal para testear |
| **pytest** | `test_*.py`, `assert`, leer fallos, `parametrize` |
| **Regresión** | Por qué el test te salva cuando refactorizás |

---

## Estructura

```
07-testing-unitario/
├── README.md                 # este archivo
├── MATERIAL_PREVIO.md        # lectura pre-clase (aula invertida)
├── GUIA_ALUMNO.md            # ejercicio guiado por fases + autoevaluación
├── PUESTA_EN_COMUN.md        # consigna de puesta en común + clave docente
└── backend/
    ├── pyproject.toml        # uv + fastapi + pytest
    ├── app/
    │   ├── rules.py          # 🔒 funciones PURAS de autorización (las del 06)
    │   ├── password.py       # 🔒 funciones PURAS de validación
    │   └── main.py           # mini-app FastAPI que las USA (no se testea acá)
    └── tests/
        ├── test_password.py  # ✅ referencia: tests completos que pasan
        └── test_rules.py     # 🔓 ejercicio: tests con TODO para completar
```

---

## Cómo arrancar

```bash
cd 07-testing-unitario/backend
uv sync            # instala fastapi + pytest
uv run pytest      # corre los tests
```

Vas a ver algo así:

```
tests/test_password.py ......                                    [ 50%]
tests/test_rules.py ..FFFF                                      [100%]
========================= 8 passed, 4 failed =========================
```

- Los `.` son tests que **pasan**.
- Las `F` son tests que **fallan** — son los `TODO` que tenés que completar
  en la guía.

---

## Por qué acá NO hay base de datos

Fijate que este módulo **no levanta postgres**. No es un descuido: es **la
lección central del test unitario**. Un unitario testea **una unidad aislada**
(una función), sin tocar la base, la red, el sistema de archivos ni el reloj.
Si tu test necesita postgres, ya no es unitario — es de **integración**, y eso
es tema del próximo módulo.

> La gracia del unitario es que corre **rápido y determinista**: milisegundos,
> sin Docker, sin estado. Por eso es la base de la pirámide de testing.

---

> **Único objetivo del módulo**: que salgas sabiendo escribir un test que
> verifique una función, y entendiendo **por qué** eso te hace un profesional
> mejor. Ponete las pilas: el test lo escribís una vez y te cuida para siempre.
