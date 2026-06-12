import bleach
import markdown
from schemas.models import db, Role, ReviewStatus, Genre, User
from werkzeug.security import generate_password_hash
import os
import hashlib
import uuid

ALLOWED_TAGS = [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'strike', 'del', 'ins',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'pre', 'code',
    'blockquote', 'a', 'img', 'span', 'div', 'table', 'thead', 'tbody',
    'tr', 'th', 'td'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title'],
    'span': ['class'],
    'div': ['class'],
    'code': ['class'],
    'pre': ['class'],
    'th': ['colspan', 'rowspan'],
    'td': ['colspan', 'rowspan']
}


def sanitize_html(html_content):
    return bleach.clean(
        html_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )


def markdown_to_html(markdown_text):
    html = markdown.markdown(
        markdown_text,
        extensions=['extra', 'codehilite', 'nl2br']
    )
    return sanitize_html(html)


def init_db(app):
    """Initialize database with default data"""
    with app.app_context():
        db.create_all()

        # Initialize roles
        roles = [
            {'name': 'Администратор', 'description': 'Суперпользователь, имеет полный доступ к системе'},
            {'name': 'Модератор', 'description': 'Может редактировать данные книг и производить модерацию рецензий'},
            {'name': 'Пользователь', 'description': 'Может оставлять рецензии'}
        ]

        for role_data in roles:
            if not Role.query.filter_by(name=role_data['name']).first():
                role = Role(**role_data)
                db.session.add(role)

        # Initialize review statuses
        statuses = [
            {'name': 'На рассмотрении', 'description': 'Рецензия ожидает модерации'},
            {'name': 'Одобрена', 'description': 'Рецензия одобрена и опубликована'},
            {'name': 'Отклонена', 'description': 'Рецензия отклонена модератором'}
        ]

        for status_data in statuses:
            if not ReviewStatus.query.filter_by(name=status_data['name']).first():
                status = ReviewStatus(**status_data)
                db.session.add(status)

        # Initialize genres
        genres = [
            'Роман', 'Детектив', 'Фантастика', 'Фэнтези', 'Научная литература',
            'Поэзия', 'Драма', 'Комедия', 'Триллер', 'Ужасы', 'Биография',
            'История', 'Философия', 'Психология', 'Саморазвитие', 'Детская литература'
        ]

        for genre_name in genres:
            if not Genre.query.filter_by(name=genre_name).first():
                genre = Genre(name=genre_name)
                db.session.add(genre)

        db.session.commit()

        # Create admin user
        admin_role = Role.query.filter_by(name='Администратор').first()
        if admin_role and not User.query.filter_by(login='admin').first():
            admin = User()
            admin.login = 'admin'
            admin.password_hash = generate_password_hash('admin123')
            admin.last_name = 'Администратор'
            admin.first_name = 'Системы'
            admin.patronymic = None
            admin.role_id = admin_role.id
            db.session.add(admin)
            db.session.commit()

        # Create moderator user (optional, for testing)
        moderator_role = Role.query.filter_by(name='Модератор').first()
        if moderator_role and not User.query.filter_by(login='moderator').first():
            moderator = User()
            moderator.login = 'moderator'
            moderator.password_hash = generate_password_hash('moderator123')
            moderator.last_name = 'Модераторов'
            moderator.first_name = 'Модератор'
            moderator.patronymic = None
            moderator.role_id = moderator_role.id
            db.session.add(moderator)
            db.session.commit()

        # Create regular user (optional, for testing)
        user_role = Role.query.filter_by(name='Пользователь').first()
        if user_role and not User.query.filter_by(login='user').first():
            user = User()
            user.login = 'user'
            user.password_hash = generate_password_hash('user123')
            user.last_name = 'Пользователь'
            user.first_name = 'Обычный'
            user.patronymic = None
            user.role_id = user_role.id
            db.session.add(user)
            db.session.commit()


def save_uploaded_file(file, upload_folder):
    """Сохраняет загруженный файл и возвращает имя файла"""
    if not file:
        return None

    # Вычисляем MD5 хэш
    file_content = file.read()
    md5_hash = hashlib.md5(file_content).hexdigest()
    file.seek(0)

    # Получаем расширение файла
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'

    # Генерируем уникальное имя файла
    filename = f"{uuid.uuid4().hex}.{ext}"

    # Сохраняем файл
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    return filename, md5_hash