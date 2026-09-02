"""
Capa de negocio (Service) — los casos de uso de autenticación.

COMPLETÁ los métodos marcados con TODO. El service aplica las reglas de
negocio y delega el acceso a datos en el repository.

LAS DECISIONES CLAVE DE HOY (leelas antes de codear):

    1. ¿Dónde se hashea la contraseña? → ACÁ (en el service), no en el
       controller ni en el repository. Hashear es una regla de negocio:
       "todo usuario que se crea, se crea con su contraseña protegida".

    2. ¿El service devuelve un 401/409? → NO. El service NO sabe de HTTP.
       Devuelve `None` para decir "no se pudo" y el controller decide qué
       status code corresponde. Igual que el 404 del Módulo 03.

    3. Timing attack / user enumeration (bonus 🎯): si en el login
       respondés distinto según si el email existe o no, le estás dando al
       atacante una forma de averiguar qué emails están registrados. Por eso
       el login ante "usuario inexistente" y ante "contraseña incorrecta"
       debe tardar lo MISMO y devolver el MISMO mensaje.
"""

from app.models.user import User, UserCreate
from app.repositories.user_repository import UserRepository
from app.security import hash_password, verify_password


class AuthService:
    """Casos de uso de autenticación: register y login."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register_user(self, body: UserCreate) -> User | None:
        """
        Registra un usuario nuevo. Devuelve el User creado, o None si el
        email ya está en uso.

        Pasos (desarrollá cada uno):
          1. Normalizá el email: `body.email.lower().strip()`.
             (Es una regla de negocio: "los emails son case-insensitive".
              Evita que "Juan@X.com" y "juan@x.com" sean dos cuentas.)
          2. Si `repository.get_by_email(email)` devuelve algo → devolvé None.
          3. Hasheá la contraseña con `hash_password(body.password)`.
          4. Devolvé `repository.create(email, hashed)`.
        """
        raise NotImplementedError("TODO: implementar register_user")

    def authenticate_user(self, email: str, password: str) -> User | None:
        """
        Verifica credenciales. Devuelve el User si son válidas, None si no.

        Pasos:
          1. Normalizá el email igual que en register.
          2. Buscá el user: `user = self.repository.get_by_email(email)`.
          3. Si `user is None` → devolvé None (no hay nada que verificar).
          4. Si `verify_password(password, user.hashed_password)` es False
             → devolvé None.
          5. Devolvé el user.

        🎯 Bonus (timing attack): si el usuario no existe, el paso 3 devuelve
        al toque, y el paso 4 (que verifica un hash de Argon2, lento) ni
        corre. Eso hace que "email inexistente" sea más RÁPIDO que
        "contraseña mal", y un atacante puede medir la diferencia. Para
        arreglarlo se verifica SIEMPRE contra un hash falso cuando el user
        no existe, así el tiempo es constante. Investigá: ¿cómo lo harías?
        (Pista: `hash_password("dummy")` una sola vez, y verificá contra eso.)
        """
        raise NotImplementedError("TODO: implementar authenticate_user")

    def count_users(self) -> int:
        # EJEMPLO resuelto — el health check usa este método.
        return self.repository.count()
