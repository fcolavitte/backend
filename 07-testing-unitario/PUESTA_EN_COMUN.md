# 🎤 Puesta en común — Módulo 07 (consigna + clave)

> Cierre de la clase de aula invertida. Cada alumno expone su trabajo en
> **60-90 segundos** y responde preguntas. El objetivo no es "mostrar que los
> tests pasan", es **verificar que entiende lo que hizo**.

---

## Para el alumno — qué preparar

Antes de la puesta en común, asegurate de poder hacer estas **3 cosas**:

1. **Mostrar en vivo** (30 seg)
   - Corré `uv run pytest` y mostrá que **todo pasa en verde**.
   - Abrí **un test que hayas escrito vos** (Fase 2 o Fase 4) y señalá las tres
     fases AAA.

2. **Explicar un concepto** (30 seg) — el docente elige entre:
   - Qué es una **función pura** y por qué es fácil de testear.
   - Por qué este módulo **no toca la base de datos**.
   - Qué es el **TDD** (rojo → verde → refactor).

3. **Responder preguntas** (30 seg) — las de la autoevaluación de la guía.

### El guion (para que no improvises)

> 1. "Corro pytest y tengo N tests en verde" → mostrás el comando.
> 2. "Este test que escribí verifica que..." → señalás AAA sobre tu test.
> 3. "Elijo hablar de..." → un concepto.

---

## Para el docente — qué buscar en cada respuesta

### Clave del quiz de autoevaluación

| Pregunta | Respuesta esperada | Señal de alerta (no entendió) |
|---|---|---|
| ¿Qué es un test unitario? | Verifica **una unidad aislada** (una función) | Dice "probar la app" o "ver si anda todo" |
| ¿Qué es AAA? | Arrange (preparar) · Act (llamar) · Assert (verificar) | No puede nombrar las tres |
| ¿Por qué no hay DB? | Unitario = aislado, sin IO; la DB es integración | Dice "no hacía falta" o "me olvidé" |
| ¿Función pura? | Determinista + sin efectos colaterales | Confunde "pura" con "simple" o "corta" |
| ¿Verde = está bien? | No: solo verifica el comportamiento que **yo** definí | Dice "sí, verde = correcto" sin matiz |
| ¿Unitario vs integración? | Unitario = una función aislada; integración = varios componentes + DB real | No distingue los dos |

### Señales de "pasó verde pero no entendió"

- Completó los `TODO` pero **no puede decir qué comportamiento** verifica cada uno.
- No puede señalar las **tres fases AAA** sobre su propio test.
- Cree que **verde = "el código está correcto"**, sin matices.
- No sabe decir **por qué no hay postgres**.

> Si detectás alguna de estas señales, es un alumno que hizo el ejercicio
> mecánicamente. Ahí es donde la puesta en común justifica existir: lo que el
> pytest no puede evaluar, vos sí.

### Preguntas de profundización (para el que responde bien)

1. Si mañana alguien cambia `can_edit` y tu test **sigue verde**, ¿eso es bueno o malo?
2. `can_publish` y `can_edit` son idénticas hoy. ¿Por qué igual conviene tener las dos separadas?
3. ¿Dónde pondrías un test: en la **lógica pura** o en el **endpoint de FastAPI**? ¿Por qué?
4. ¿Qué es un **falso verde** y cómo lo evitarías?

---

> **Criterio de cierre**: un alumno que corre pytest en verde pero no puede
> explicar su test **no cumplió la consigna**. El test es el medio; la
> comprensión es el fin. Que salgan de la clase diciendo *"verde no es sinónimo
> de correcto"* — esa frase vale más que 20 tests pasando.
