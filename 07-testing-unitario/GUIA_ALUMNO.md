# 🧭 Guía del alumno — Testing unitario (ejercicio por fases)

> Hacé las fases **en orden**. No saltes a escribir código sin leer cada fase:
> el objetivo no es "que pasen los tests", es **entender qué estás verificando**.

---

## Fase 0 · Preparar el entorno y ver el estado inicial

```bash
cd 07-testing-unitario/backend
uv sync
uv run pytest
```

Vas a ver **6 tests que pasan** (`.`) y **4 que fallan** (`F`). Los que fallan
son los `TODO` de `tests/test_rules.py`. Ese es el punto de partida.

> 🧠 **Antes de seguir, mirá un test que PASA** (`tests/test_password.py`) y
> uno que FALLA (`tests/test_rules.py`). Identificá las tres fases AAA en cada
> uno. Si no las ves, volvé al material previo sección 5.

---

## Fase 1 · Completar los tests de autorización

Abrí `tests/test_rules.py`. Hay 4 funciones con `assert False, "TODO..."`.
Tu trabajo es **reemplazar cada TODO por los asserts correctos**.

Mirá la referencia ya completa para copiar el patrón:

```python
def test_scope_allows_write_con_write():
    assert scope_allows_write("read write") is True

def test_scope_allows_write_solo_read():
    assert scope_allows_write("read") is False
```

Y ahora completá, por ejemplo, `test_can_manage_users_solo_admin`:

```python
def test_can_manage_users_solo_admin():
    # TODO: assert que can_manage_users("admin") es True
    # TODO: assert que can_manage_users("viewer") es False
    assert can_manage_users("admin") is True
    assert can_manage_users("viewer") is False
```

**Reglas para completar bien:**

1. Un test = **un comportamiento**, no "probar todo junto". Si un test verifica
   admin *y* viewer *y* editor, está mal: separalo.
2. Pensá el **caso de borde**: ¿qué pasa con el rol vacío `""`? ¿Y con
   `scope = ""` (sin espacios)?
3. Corré `uv run pytest` después de cada test. El objetivo es verlo pasar.

### Completá los 4 TODO

| Test | Qué comportamiento verifica |
|------|-----------------------------|
| `test_can_manage_users_solo_admin` | solo admin gestiona usuarios |
| `test_can_delete_solo_admin` | solo admin borra documentos |
| `test_can_edit_dueño_puede` | el dueño siempre edita lo suyo |
| `test_can_edit_editor_no_puede_sobre_ajeno` | un editor NO edita lo ajeno |

> ⚠️ Ojo con `can_edit`: tiene **dos** caminos (dueño OR admin). Asegurate de
> testear **los dos** y el caso negativo (ni dueño ni admin).

---

## Fase 2 · Escribí tests nuevos (TDD en miniatura)

Ahora no completás: **escribís** el test de una función que todavía no existe.

1. Abrí `app/rules.py`. Fijate que **falta** `can_publish` (en el módulo 06
   existía, acá la sacamos a propósito).
2. Creá `tests/test_publish.py` y escribí **primero el test** (esto es TDD:
   el test define el comportamiento deseado):

```python
from app.rules import can_publish

def test_can_publish_dueño_puede():
    assert can_publish(owner_id=5, user_id=5, role="editor") is True

def test_can_publish_admin_puede_sobre_ajeno():
    assert can_publish(owner_id=5, user_id=9, role="admin") is True

def test_can_publish_editor_no_puede_sobre_ajeno():
    assert can_publish(owner_id=5, user_id=9, role="editor") is False
```

3. Corré `uv run pytest` → los 3 tests **fallan** porque `can_publish` no existe.
4. Ahora **escribí la función** en `app/rules.py`:

```python
def can_publish(owner_id: int, user_id: int, role: str) -> bool:
    return owner_id == user_id or role == "admin"
```

5. Corré de nuevo → **verde**. Eso es TDD: rojo → verde → (refactor).

> 🧠 **Pregunta para la defensa**: ¿`can_publish` es igual que `can_edit`?
> ¿Vale la pena tener las dos por separado aunque hoy sean idénticas? ¿Por qué?

---

## Fase 3 · Parametrize (bonus)

Reescribí `test_can_delete_solo_admin` de la Fase 1 usando `parametrize`:

```python
import pytest
from app.rules import can_delete

@pytest.mark.parametrize("role,esperado", [
    ("admin", True),
    ("editor", False),
    ("viewer", False),
])
def test_can_delete_por_rol(role, esperado):
    assert can_delete(role) is esperado
```

Corré y mirá que pytest lo muestra como **3 tests**. Ventaja: agregar un caso
nuevo (p. ej. `("", False)`) es una línea, no un test entero.

---

## Fase 4 · Casos de borde (el nivel 🔴)

Los buenos testers no testean solo el "camino feliz". Buscá casos raros:

1. En `scope_allows_write`: ¿qué pasa con `"write "` (espacio al final)?
   ¿Y con `"WRITE"` (mayúscula)? ¿Debería importar? Escribí el test y decidí.
2. En `validate_password` (`app/password.py`): ¿qué pasa con `""` (vacía)?
   ¿Y con una contraseña que tiene solo números? Escribí esos tests.
3. En `can_edit`: ¿qué pasa si `owner_id == user_id` **y** el rol es `"viewer"`
   (el dueño es viewer)? Según la regla, ¿puede editar lo suyo? Escribí el test
   y verificá que la función haga lo que la matriz del 06 dice.

---

## Checklist de cierre (mostralo al docente)

- [ ] Corro `uv run pytest` y **todos los tests pasan** (sin `F`).
- [ ] Sé explicar las **tres fases de AAA** sobre un test mío.
- [ ] Escribí al menos **un test nuevo** en la Fase 2 (TDD).
- [ ] Usé `parametrize` al menos una vez (Fase 3).
- [ ] Testeé al menos **un caso de borde** (Fase 4).
- [ ] Sé decir por qué **no hay postgres** en este módulo.

---

## Autoevaluación — antes de la puesta en común

Respondé estas preguntas **con tus palabras** (no de memoria). Si alguna te
cuesta, volvé a la sección correspondiente del material previo. Son exactamente
las que te van a hacer en la puesta en común.

1. **¿Qué es un test unitario?** Definilo sin decir "es una función que testea código".
2. **¿Qué significan las tres fases AAA?** Nombrá cada una y qué hace.
3. **¿Por qué este módulo no usa base de datos (postgres)?**
4. **¿Qué es una función pura?** Da un ejemplo de función pura y uno de impura.
5. **Si un test pasa en verde, ¿significa que el código "está bien"?** Explicá.
6. **¿Qué diferencia hay entre un test unitario y uno de integración?**

> No sigas hasta poder responder las 6 sin titubear. El objetivo de la puesta
> en común es que **expliques tu razonamiento**, no que leas tu código.

---

> **Cierre**: un test no demuestra que el código "está bien". Demuestra que se
> comporta como vos definiste que debe comportarse. La pregunta no es "¿pasa?",
> es "**¿estoy verificando el comportamiento correcto?**". Esa distinción es la
> que separa un profesional de alguien que "corre pytest hasta que sale verde".
