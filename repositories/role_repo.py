from schemas.models import Role
from .base_repo import BaseRepository

class RoleRepository(BaseRepository):
    def get_by_id(self, role_id):
        return Role.query.get(role_id)

    def get_by_name(self, name):
        return Role.query.filter_by(name=name).first()

    def get_all(self):
        return Role.query.all()
