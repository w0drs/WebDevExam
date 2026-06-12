from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from datetime import datetime

from config import Config
from schemas.models import db
from repositories.role_repo import RoleRepository
from repositories.user_repo import UserRepository
from repositories.genre_repo import GenreRepository
from repositories.book_repo import BookRepository
from repositories.cover_repo import CoverRepository
from repositories.review_repo import ReviewRepository, ReviewStatusRepository
from services.auth_services import AuthService
from services.book_service import BookService
from services.cover_service import CoverService
from services.review_service import ReviewService
from services.moderation_service import ModerationService
from scripts.utils import init_db, markdown_to_html, sanitize_html

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize repositories
user_repo = UserRepository(db)
role_repo = RoleRepository(db)
book_repo = BookRepository(db)
genre_repo = GenreRepository(db)
cover_repo = CoverRepository(db)
review_repo = ReviewRepository(db)
review_status_repo = ReviewStatusRepository(db)

# Initialize services
auth_service = AuthService(user_repo, role_repo)
book_service = BookService(book_repo, genre_repo, cover_repo, review_repo, db)
cover_service = CoverService(cover_repo, app.config['UPLOAD_FOLDER'])
review_service = ReviewService(review_repo, review_status_repo, db)
moderation_service = ModerationService(review_repo, review_status_repo, db)


@login_manager.user_loader
def load_user(user_id):
    return user_repo.get_by_id(int(user_id))


@app.context_processor
def inject_now():
    return {'now': datetime.now()}


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books, total = book_service.get_paginated_books(page, app.config['BOOKS_PER_PAGE'])

    for book in books:
        book.avg_rating = review_service.get_average_rating(book.id)
        book.reviews_count = review_service.get_approved_reviews_count(book.id)

    return render_template('index.html',
                         books=books,
                         page=page,
                         total=total,
                         books_per_page=app.config['BOOKS_PER_PAGE'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        # Используем существующий auth_service
        user = auth_service.authenticate(username, password)

        if user:
            login_user(user, remember=remember)
            flash(f'Добро пожаловать, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


@app.route('/book/add', methods=['GET', 'POST'])
@login_required
def add_book():
    print("\n=== ADD BOOK CALLED ===")
    print(f"Method: {request.method}")
    print(f"Current user: {current_user.login}")
    print(f"User role: {current_user.role_rel.name if current_user.role_rel else 'None'}")

    if not current_user.has_role('Администратор'):
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))

    genres = genre_repo.get_all()

    if request.method == 'POST':
        print("\n=== POST DATA RECEIVED ===")
        print(f"Form keys: {list(request.form.keys())}")
        print(f"Files keys: {list(request.files.keys())}")

        title = request.form.get('title')
        description = request.form.get('description')
        year = request.form.get('year')
        publisher = request.form.get('publisher')
        author = request.form.get('author')
        pages = request.form.get('pages')
        selected_genres = request.form.getlist('genres')
        cover_file = request.files.get('cover')

        print(f"title: {title}")
        print(f"author: {author}")
        print(f"year: {year}")
        print(f"publisher: {publisher}")
        print(f"pages: {pages}")
        print(f"selected_genres: {selected_genres}")
        print(f"cover_file: {cover_file.filename if cover_file else 'None'}")

        if not all([title, description, year, publisher, author, pages]):
            print("Missing required fields!")
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('book_form.html', book=None, genres=genres, selected_genres=[])

        try:
            print("Creating book...")
            book = book_service.create_book(
                title=title,
                description=sanitize_html(description),
                year=int(year),
                publisher=publisher,
                author=author,
                pages=int(pages),
                genre_ids=[int(g) for g in selected_genres] if selected_genres else []
            )
            print(f"Book created with ID: {book.id}")

            if cover_file and cover_file.filename:
                print(f"Saving cover: {cover_file.filename}")
                cover = cover_service.save_cover(cover_file, book.id)
                if cover:
                    book_service.update_book_cover(book.id, cover.id)
                    print(f"Cover saved with ID: {cover.id}")

            db.session.commit()
            flash('Книга успешно добавлена', 'success')
            return redirect(url_for('book_detail', book_id=book.id))

        except Exception as e:
            db.session.rollback()
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('book_form.html', book=None, genres=genres, selected_genres=selected_genres)

    print("Rendering book_form.html")
    return render_template('book_form.html', book=None, genres=genres, selected_genres=[])


@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not (current_user.has_role('Администратор') or current_user.has_role('Модератор')):
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))

    book = book_repo.get_by_id(book_id)
    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('index'))

    genres = genre_repo.get_all()
    current_genres = [g.id for g in book.genres]

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        year = request.form.get('year')
        publisher = request.form.get('publisher')
        author = request.form.get('author')
        pages = request.form.get('pages')
        selected_genres = request.form.getlist('genres')

        if not all([title, description, year, publisher, author, pages]):
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('book_form.html', book=book, genres=genres, selected_genres=current_genres)

        try:
            book_service.update_book(
                book_id=book_id,
                title=title,
                description=sanitize_html(description),
                year=int(year),
                publisher=publisher,
                author=author,
                pages=int(pages),
                genre_ids=[int(g) for g in selected_genres]
            )

            flash('Книга успешно обновлена', 'success')
            return redirect(url_for('book_detail', book_id=book.id))

        except Exception as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return render_template('book_form.html', book=book, genres=genres, selected_genres=selected_genres)

    return render_template('book_form.html', book=book, genres=genres, selected_genres=current_genres)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
@login_required
def delete_book(book_id):
    if not current_user.has_role('Администратор'):
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))

    book = book_repo.get_by_id(book_id)
    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('index'))

    try:
        if book.cover:
            cover_service.delete_cover_file(book.cover.filename)

        book_service.delete_book(book_id)
        flash('Книга успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении книги', 'danger')

    return redirect(url_for('index'))


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = book_repo.get_by_id(book_id)
    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('index'))

    reviews = review_repo.get_by_book_and_status(book_id, 'Одобрена')

    can_review = False
    user_review = None
    if current_user.is_authenticated and current_user.has_role('Пользователь'):
        user_review = review_repo.get_by_user_and_book(current_user.id, book_id)
        if not user_review:
            can_review = True

    avg_rating = review_service.get_average_rating(book_id)
    book.description_html = markdown_to_html(book.description)

    return render_template('book_detail.html',
                           book=book,
                           reviews=reviews,
                           avg_rating=avg_rating,
                           can_review=can_review,
                           user_review=user_review)


@app.route('/book/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    if not current_user.has_role('Пользователь'):
        flash('Только пользователи могут оставлять рецензии', 'danger')
        return redirect(url_for('book_detail', book_id=book_id))

    book = book_repo.get_by_id(book_id)
    if not book:
        flash('Книга не найдена', 'danger')
        return redirect(url_for('index'))

    existing_review = review_repo.get_by_user_and_book(current_user.id, book_id)
    if existing_review:
        flash('Вы уже оставили рецензию на эту книгу', 'warning')
        return redirect(url_for('book_detail', book_id=book_id))

    if request.method == 'POST':
        rating = request.form.get('rating')
        text = request.form.get('text')

        if not rating or not text:
            flash('Пожалуйста, заполните все поля', 'danger')
            return render_template('review_form.html', book=book)

        try:
            review_service.create_review(
                book_id=book_id,
                user_id=current_user.id,
                rating=int(rating),
                text=sanitize_html(text)
            )

            flash('Рецензия отправлена на модерацию', 'success')
            return redirect(url_for('book_detail', book_id=book_id))

        except Exception as e:
            db.session.rollback()
            flash('Ошибка при сохранении рецензии', 'danger')
            return render_template('review_form.html', book=book)

    return render_template('review_form.html', book=book)


@app.route('/my-reviews')
@login_required
def my_reviews():
    if not current_user.has_role('Пользователь'):
        flash('Доступ запрещён', 'danger')
        return redirect(url_for('index'))

    reviews = review_repo.get_by_user(current_user.id)
    return render_template('my_reviews.html', reviews=reviews)


@app.route('/moderate')
@login_required
def moderate_reviews():
    if not current_user.has_role('Модератор'):
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    reviews, total = moderation_service.get_pending_reviews(page, app.config['REVIEWS_PER_PAGE'])

    return render_template('moderate_reviews.html',
                         reviews=reviews,
                         page=page,
                         total=total,
                         reviews_per_page=app.config['REVIEWS_PER_PAGE'])


@app.route('/moderate/<int:review_id>')
@login_required
def moderate_review_detail(review_id):
    if not current_user.has_role('Модератор'):
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))

    review = review_repo.get_by_id(review_id)
    if not review:
        flash('Рецензия не найдена', 'danger')
        return redirect(url_for('moderate_reviews'))

    return render_template('moderate_review_detail.html', review=review)


@app.route('/moderate/<int:review_id>/approve', methods=['POST'])
@login_required
def approve_review(review_id):
    if not current_user.has_role('Модератор'):
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))

    try:
        moderation_service.approve_review(review_id)
        flash('Рецензия одобрена', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при одобрении рецензии', 'danger')

    return redirect(url_for('moderate_reviews'))


@app.route('/moderate/<int:review_id>/reject', methods=['POST'])
@login_required
def reject_review(review_id):
    if not current_user.has_role('Модератор'):
        flash('У вас недостаточно прав для выполнения данного действия', 'danger')
        return redirect(url_for('index'))

    try:
        moderation_service.reject_review(review_id)
        flash('Рецензия отклонена', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при отклонении рецензии', 'danger')

    return redirect(url_for('moderate_reviews'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_db(app)
    app.run(debug=True, host='0.0.0.0', port=5000)