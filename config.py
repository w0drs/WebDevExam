import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

    # Database - PostgreSQL
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '12345')
    DB_NAME = os.environ.get('DB_NAME', 'electronic_library')

    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

    # Pagination
    BOOKS_PER_PAGE = int(os.environ.get('BOOKS_PER_PAGE', 10))
    REVIEWS_PER_PAGE = int(os.environ.get('REVIEWS_PER_PAGE', 10))