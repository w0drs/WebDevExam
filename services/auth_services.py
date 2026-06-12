from werkzeug.security import generate_password_hash, check_password_hash
from schemas.models import User


class AuthService:
    def __init__(self, user_repo, role_repo):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def authenticate(self, login, password):
        print(f"\n[AUTH SERVICE] authenticate('{login}', '{password}')")
        user = self.user_repo.get_by_login(login)

        if not user:
            print(f"[AUTH SERVICE] Пользователь '{login}' не найден")
            return None

        print(f"[AUTH SERVICE] Пользователь найден: {user.login}")
        print(f"[AUTH SERVICE] Хэш из БД: {user.password_hash[:60]}...")

        result = check_password_hash(user.password_hash, password)
        print(f"[AUTH SERVICE] Результат check_password_hash: {result}")

        if user and result:
            print(f"[AUTH SERVICE] Аутентификация успешна для {login}")
            return user

        print(f"[AUTH SERVICE] Аутентификация не удалась для {login}")
        return None

    def register(self, login, password, last_name, first_name, patronymic, role_name='Пользователь'):
        role = self.role_repo.get_by_name(role_name)
        if not role:
            raise ValueError(f"Role {role_name} not found")

        # Create user using dictionary unpacking or direct assignment
        user = User()
        user.login = login
        user.password_hash = generate_password_hash(password)
        user.last_name = last_name
        user.first_name = first_name
        user.patronymic = patronymic
        user.role_id = role.id

        self.user_repo.add(user)
        self.user_repo.commit()
        return user