class ModerationService:
    def __init__(self, review_repo, review_status_repo, db):
        self.review_repo = review_repo
        self.review_status_repo = review_status_repo
        self.db = db

    def get_pending_reviews(self, page, per_page):
        pagination = self.review_repo.get_pending_paginated(page, per_page)
        return pagination.items, pagination.total

    def approve_review(self, review_id):
        review = self.review_repo.get_by_id(review_id)
        if review:
            approved_status = self.review_status_repo.get_by_name('Одобрена')
            self.review_repo.update_status(review, approved_status.id)
            self.review_repo.commit()

    def reject_review(self, review_id):
        review = self.review_repo.get_by_id(review_id)
        if review:
            rejected_status = self.review_status_repo.get_by_name('Отклонена')
            self.review_repo.update_status(review, rejected_status.id)
            self.review_repo.commit()
