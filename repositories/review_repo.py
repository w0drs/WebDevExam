from .base_repo import BaseRepository
from schemas.models import Review, ReviewStatus
from sqlalchemy import desc


class ReviewRepository(BaseRepository):
    def get_by_id(self, review_id):
        return Review.query.get(review_id)

    def get_by_user(self, user_id):
        return Review.query.filter_by(user_id=user_id).order_by(desc(Review.created_at)).all()

    def get_by_book(self, book_id):
        return Review.query.filter_by(book_id=book_id).order_by(desc(Review.created_at)).all()

    def get_by_book_and_status(self, book_id, status_name):
        return Review.query.join(ReviewStatus).filter(
            Review.book_id == book_id,
            ReviewStatus.name == status_name
        ).order_by(desc(Review.created_at)).all()

    def get_by_user_and_book(self, user_id, book_id):
        return Review.query.filter_by(user_id=user_id, book_id=book_id).first()

    def get_pending_paginated(self, page, per_page, status_name='На рассмотрении'):
        return Review.query.join(ReviewStatus).filter(
            ReviewStatus.name == status_name
        ).order_by(Review.created_at).paginate(page=page, per_page=per_page, error_out=False)

    def create(self, book_id, user_id, rating, text, status_id):
        review = Review(
            book_id=book_id,
            user_id=user_id,
            rating=rating,
            text=text,
            status_id=status_id
        )
        self.add(review)
        return review

    def update_status(self, review, status_id):
        review.status_id = status_id
        return review


class ReviewStatusRepository(BaseRepository):
    def get_by_id(self, status_id):
        return ReviewStatus.query.get(status_id)

    def get_by_name(self, name):
        return ReviewStatus.query.filter_by(name=name).first()

    def get_all(self):
        return ReviewStatus.query.all()
