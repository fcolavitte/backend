# 📖 Material previo — Testing unitario (lectura pre-clase)

> Tiempo estimado: 30-40 minutos. Leelo ANTES de la clase (aula invertida).
> En clase lo vas a aplicar en el ejercicio de la `GUIA_ALUMNO.md`.

---

## 1 · El problema que resuelve testear

Pensá en el módulo 06: para verificar la matriz de autorización corrías
`verificar_authz.sh` — 44 checks a mano, con curl, contra un server levantado.
Cada vez que tocabas una línea, tenías que correr **todo de nuevo** y mirar
con tus ojos si seguía bien.

Eso tiene tres problemas:

1. **No escala**: 44 checks hoy, ¿400 mañana? Imposible de verificar a ojo.
2. **Frío**: no detecta lo que *no se te ocurrió* probar (el caso de borde).
3. **Se pierde**: si yo cambio tu código, no tengo tu checklist mental para
   saber si lo rompí.

**El test automatizado resuelve los tres**: es un programa que ejecuta tu
código y **falla** si el resultado no es el esperado. Lo corrés en un segundo,
las veces que quieras, y guarda tu conocimiento sobre "cómo debe comportarse".

---

## 2 · Qué es un test unitario

Un **test unitario** verifica **una unidad** de código — normalmente **una
función** (o un método de una clase) — **de forma aislada**.

"Unidad" + "aislada" son las dos palabras clave:

- **Unidad**: testea una sola cosa, no "todo el flujo". Si testea 3 funciones
  a la vez y falla, no sabés cuál rompió.
- **Aislada**: no depende de la base de datos, ni de la red, ni del sistema de
  archivos, ni del reloj. Le das argumentos y mirás el valor de retorno.

```python
# Esto es una función pura: misma entrada → misma salida, sin efectos colaterales
def can_edit(owner_id: int, user_id: int, role: str) -> bool:
    return owner_id == user_id or role == "admin"
```

Un test unitario de esa función:

```python
def test_can_edit_dueño_puede():
    assert can_edit(owner_id=5, user_id=5, role="editor") is True
```

Eso es todo. No hay server, no hay DB, no hay token. **Datos adentro, resultado
afuera, comparás.**

---

## 3 · La pirámide de testing

```
        ▲         ┌─────────────┐
     costoso      │    E2E      │   pocos: flujo completo con UI/browser
     lento        ├─────────────┤
                  │ Integración │   algunos: varios componentes + DB real
     barato       ├─────────────┤
     rápido       │  UNITARIOS  │   MUCHOS: una función aislada
        ▼         └─────────────┘
```

- **Unitarios** (base): miles, rápidos, sin DB. Este módulo.
- **Integración** (medio): testean que dos piezas conversan (ej. tu código +
  PostgreSQL). Próximo módulo.
- **E2E** (cima): el flujo completo desde la UI, como un usuario real. Pocos.

**Regla de oro**: cuanto más abajo en la pirámide, más barato y más tests
escribís. Si tenés que elegir dónde poner un test, ponelo lo más abajo posible.

---

## 4 · Función pura: el caso ideal

Una **función pura** es la que cumple dos cosas:

1. **Determinista**: misma entrada → misma salida, siempre.
2. **Sin efectos colaterales**: no modifica el mundo (no escribe en DB, no
   manda mails, no muta estado global).

¿Por qué son el sueño de testear? Porque **no necesitás preparar nada** para
probarlas. No hay que levantar postgres, ni mockear nada, ni limpiar estado.
Llamás y listo.

```python
# PURA: fácil de testear
def scope_allows_write(scope: str) -> bool:
    return "write" in scope.split()

# IMPURA: difícil de testear (escribe en la base)
def crear_documento(db, body):        # → necesita una DB real o un mock
    ...
```

**Lección central del módulo**: mientras más código puro tengas, más fácil es
testearlo. Y por eso la arquitectura en capas del módulo 03 separa "lógica"
(Service) de "IO" (Repository): la lógica tiende a ser pura y testeable, la IO
se aísla.

> Acá entra la mención a postgres: **un test unitario NO toca la base de
> datos.** Si tu función lee o escribe en postgres, para testearla tenés dos
> caminos (ambos de otro módulo): mockear la DB, o test de integración con una
> DB de test. Por eso este módulo testea funciones puras y no levanta postgres.

---

## 5 · AAA: la estructura de todo test

Todo test unitario tiene tres fases:

| Fase | Qué hacés | Ejemplo |
|------|-----------|---------|
| **A**rrange | Preparás los datos de entrada | `scope = "read write"` |
| **A**ct | Llamás a la función bajo test | `resultado = scope_allows_write(scope)` |
| **A**ssert | Verificás el resultado | `assert resultado is True` |

```python
def test_scope_allows_write_con_write():
    # Arrange
    scope = "read write"

    # Act
    resultado = scope_allows_write(scope)

    # Assert
    assert resultado is True
```

Si separás mentalmente las tres fases, escribir un test se vuelve mecánico.

---

## 6 · pytest en 5 minutos

`pytest` es EL framework de testing de Python. Lo usás así:

1. **Nombre de archivo**: `test_algo.py` (empieza con `test_`).
2. **Nombre de función**: `def test_...()` (también empieza con `test_`).
3. **Verificás con `assert`**: `assert condicion, "mensaje opcional"`.
4. **Corrés**: `uv run pytest` desde la carpeta `backend/`.

```bash
$ uv run pytest
======================== test session starts =========================
collected 12 items

tests/test_password.py ......                                    [ 50%]
tests/test_rules.py ..FFFF                                      [100%]

============================== FAILURES =============================
____ test_can_manage_users_solo_admin ______________________________
    def test_can_manage_users_solo_admin():
>       assert False, "TODO: completá este test"
E       AssertionError: TODO: completá este test
======================== short test summary =========================
FAILED tests/test_rules.py::test_can_manage_users_solo_admin - AssertionError: TODO
4 failed, 8 passed in 0.04s
```

Cómo leerlo:

- **`collected N items`** → cuántos tests encontró.
- **`.`** → pasó. **`F`** → falló. **`E`** → error (excepción inesperada).
- El fallo te dice **qué archivo, qué función, qué línea** y el valor real.

Un `assert` falla cuando la condición es **falsa**. Por eso el mensaje del
fallo muestra lo que `assert` evaluó como falso.

**Dos trucos de assert:**

```python
# Comparar listas/sets sin importar el orden (solo sets)
assert set(resultado) == {"a", "b"}

# Verificar que algo está DENTRO de una lista
assert "muy corta" in errores

# Verificar que algo levanta una excepción
import pytest
with pytest.raises(ValueError):
    funcion_que_deberia_fallar()
```

---

## 7 · Fixtures y parametrize (panorama — lo usás en la guía)

**`parametrize`**: correr el mismo test con varios datos. En vez de escribir 5
tests casi idénticos, escribís uno:

```python
import pytest

@pytest.mark.parametrize("scope,esperado", [
    ("read write", True),
    ("write", True),
    ("read", False),
    ("", False),
])
def test_scope_allows_write(scope, esperado):
    assert scope_allows_write(scope) is esperado
```

Esto genera **4 tests** (uno por cada fila). Cuando uno falla, te dice **cuál
fila** (qué datos) falló. Es oro para casos de borde.

**`fixtures`**: preparar datos que varios tests comparten. Por ahora solo
necesitás saber que existen:

```python
import pytest

@pytest.fixture
def usuario_editor():
    return {"id": 5, "role": "editor"}

def test_algo(usuario_editor):
    assert usuario_editor["role"] == "editor"
```

En este módulo de introducción casi no las vas a usar (las funciones son puras
y no necesitan setup), pero es la herramienta que vas a usar cuando testees
cosas con estado en el módulo de integración.

---

## 8 · Qué NO es un test unitario (para no confundirte)

| Esto… | Es… | Por qué no es unitario |
|-------|-----|------------------------|
| Levantar FastAPI y pegarle a un endpoint | Integración | Involucra HTTP + el framework entero |
| Escribir y leer en postgres | Integración | Depende de una DB real |
| Probar el flujo completo desde la UI | E2E | Involucra browser + todo el stack |
| Testear 3 funciones juntas | Test mal diseñado | Si falla no sabés cuál rompió |

El unitario es **una función, aislada, sin IO**. Todo lo demás es otro piso de
la pirámide — igual de válido, pero más caro y más lento.

---

## Para llevar a la clase

1. Sabé definir **test unitario** con tus palabras ("una función, aislada").
2. Sabé las **tres fases de AAA**.
3. Sabé por qué **postgres no entra** en un unitario.
4. Sabé leer un fallo de pytest (archivo, función, línea, valor real).

> Si entendés esto, el ejercicio de la guía es mecánico. Si no, releé la
> sección 5 (AAA) y la 6 (pytest) antes de tocar código. El test no se escribe
> al tuntún: se piensa primero **qué comportamiento** querés verificar.
