class BookService:
    def __init__(self, book_repo, genre_repo, cover_repo, review_repo, db):
        self.book_repo = book_repo
        self.genre_repo = genre_repo
        self.cover_repo = cover_repo
        self.review_repo = review_repo
        self.db = db

    def get_paginated_books(self, page, per_page):
        pagination = self.book_repo.get_all_paginated(page, per_page)
        return pagination.items, pagination.total

    def create_book(self, title, description, year, publisher, author, pages, genre_ids):
        book = self.book_repo.create(title, description, year, publisher, author, pages)
        self.book_repo.add_genres(book, genre_ids)
        self.book_repo.commit()
        return book

    def update_book(self, book_id, title, description, year, publisher, author, pages, genre_ids):
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError("Book not found")

        self.book_repo.update(book, title, description, year, publisher, author, pages)
        self.book_repo.add_genres(book, genre_ids)
        self.book_repo.commit()
        return book

    def update_book_cover(self, book_id, cover_id):
        book = self.book_repo.get_by_id(book_id)
        if book:
            self.book_repo.update_cover(book, cover_id)
            self.book_repo.commit()

    def delete_book(self, book_id):
        book = self.book_repo.get_by_id(book_id)
        if book:
            self.book_repo.delete(book)
            self.book_repo.commit()
