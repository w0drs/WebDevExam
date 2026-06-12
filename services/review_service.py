from schemas.models import Review, ReviewStatus
from sqlalchemy import func


class ReviewService:
    def __init__(self, review_repo, review_status_repo, db):
        self.review_repo = review_repo
        self.review_status_repo = review_status_repo
        self.db = db

    def create_review(self, book_id, user_id, rating, text):
        pending_status = self.review_status_repo.get_by_name('На рассмотрении')
        review = self.review_repo.create(book_id, user_id, rating, text, pending_status.id)
        self.review_repo.commit()
        return review

    def get_average_rating(self, book_id):
        result = self.db.session.query(func.avg(Review.rating)).join(ReviewStatus).filter(
            Review.book_id == book_id,
            ReviewStatus.name == 'Одобрена'
        ).scalar()
        return round(result, 1) if result else 0

    def get_approved_reviews_count(self, book_id):
        count = self.db.session.query(func.count(Review.id)).join(ReviewStatus).filter(
            Review.book_id == book_id,
            ReviewStatus.name == 'Одобрена'
        ).scalar()
        return count or 0
