from schemas.models import User
from .base_repo import BaseRepository


class UserRepository(BaseRepository):
    def get_by_id(self, user_id):
        return User.query.get(user_id)

    def get_by_login(self, login):
        return User.query.filter_by(login=login).first()

    def get_all(self):
        return User.query.all()
