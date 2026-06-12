from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    users = db.relationship('User', back_populates='role_rel', lazy='dynamic')


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    patronymic = db.Column(db.String(100))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    role_rel = db.relationship('Role', back_populates='users')
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete-orphan')

    @property
    def full_name(self):
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic}"
        return f"{self.last_name} {self.first_name}"

    def has_role(self, role_name):
        return self.role_rel.name == role_name


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    books = db.relationship('Book', secondary='book_genres', back_populates='genres')


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.Integer, db.ForeignKey('covers.id', ondelete='SET NULL'))

    # Убираем back_populates и используем только foreign_keys
    cover = db.relationship('Cover', foreign_keys=[cover_id], uselist=False)
    genres = db.relationship('Genre', secondary='book_genres', back_populates='books')
    reviews = db.relationship('Review', back_populates='book', cascade='all, delete-orphan')


class BookGenre(db.Model):
    __tablename__ = 'book_genres'

    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)


class Cover(db.Model):
    __tablename__ = 'covers'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False, unique=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Убираем back_populates и используем только foreign_keys
    book = db.relationship('Book', foreign_keys=[book_id], uselist=False)


class ReviewStatus(db.Model):
    __tablename__ = 'review_statuses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)

    reviews = db.relationship('Review', back_populates='status_rel')


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status_id = db.Column(db.Integer, db.ForeignKey('review_statuses.id'), nullable=False)

    book = db.relationship('Book', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')
    status_rel = db.relationship('ReviewStatus', back_populates='reviews')
