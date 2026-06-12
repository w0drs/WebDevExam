from schemas.models import Book, Genre
from sqlalchemy import desc
from .base_repo import BaseRepository


class BookRepository(BaseRepository):
    def get_by_id(self, book_id):
        return Book.query.get(book_id)

    def get_all_paginated(self, page, per_page):
        return Book.query.order_by(desc(Book.year)).paginate(page=page, per_page=per_page, error_out=False)

    def get_all(self):
        return Book.query.order_by(desc(Book.year)).all()

    def create(self, title, description, year, publisher, author, pages):
        book = Book(
            title=title,
            description=description,
            year=year,
            publisher=publisher,
            author=author,
            pages=pages
        )
        self.add(book)
        return book

    def update(self, book, title, description, year, publisher, author, pages):
        book.title = title
        book.description = description
        book.year = year
        book.publisher = publisher
        book.author = author
        book.pages = pages
        return book

    def update_cover(self, book, cover_id):
        book.cover_id = cover_id
        return book

    def delete(self, book):
        self.db.session.delete(book)

    def add_genres(self, book, genre_ids):
        genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
        book.genres = genres
        return book
