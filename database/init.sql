-- database/init.sql (полная версия для ручного создания)

-- Drop database if exists (будьте осторожны!)
DROP DATABASE IF EXISTS electronic_library;

-- Create database
CREATE DATABASE electronic_library
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Russian_Russia.UTF8'
    LC_CTYPE = 'Russian_Russia.UTF8';

-- Connect to database
\c electronic_library;

-- Create tables (обычно не нужно, т.к. SQLAlchemy создаст их автоматически)
-- Но если хотите создать вручную, вот схема:

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    login VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    patronymic VARCHAR(100),
    role_id INTEGER NOT NULL REFERENCES roles(id)
);

CREATE TABLE genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE covers (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    md5_hash VARCHAR(32) NOT NULL UNIQUE,
    book_id INTEGER NOT NULL UNIQUE
);

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    year INTEGER NOT NULL,
    publisher VARCHAR(200) NOT NULL,
    author VARCHAR(200) NOT NULL,
    pages INTEGER NOT NULL,
    cover_id INTEGER REFERENCES covers(id) ON DELETE SET NULL
);

CREATE TABLE book_genres (
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, genre_id)
);

CREATE TABLE review_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_id INTEGER NOT NULL REFERENCES review_statuses(id)
);

-- Create indexes for better performance
CREATE INDEX idx_reviews_book_id ON reviews(book_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_status_id ON reviews(status_id);
CREATE INDEX idx_reviews_created_at ON reviews(created_at);
CREATE INDEX idx_books_year ON books(year);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_covers_md5_hash ON covers(md5_hash);