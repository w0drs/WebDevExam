from .base_repo import BaseRepository
from schemas.models import Genre


class GenreRepository(BaseRepository):
    def get_by_id(self, genre_id):
        return Genre.query.get(genre_id)

    def get_by_name(self, name):
        return Genre.query.filter_by(name=name).first()

    def get_all(self):
        return Genre.query.order_by(Genre.name).all()
