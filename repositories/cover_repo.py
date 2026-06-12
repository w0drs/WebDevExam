from .base_repo import BaseRepository
from schemas.models import Cover


class CoverRepository(BaseRepository):
    def get_by_id(self, cover_id):
        return Cover.query.get(cover_id)

    def get_by_md5(self, md5_hash):
        return Cover.query.filter_by(md5_hash=md5_hash).first()

    def get_by_book_id(self, book_id):
        return Cover.query.filter_by(book_id=book_id).first()

    def create(self, filename, mime_type, md5_hash, book_id):
        cover = Cover(
            filename=filename,
            mime_type=mime_type,
            md5_hash=md5_hash,
            book_id=book_id
        )
        self.add(cover)
        return cover
