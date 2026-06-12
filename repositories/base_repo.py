class BaseRepository:
    def __init__(self, db):
        self.db = db

    def add(self, entity):
        self.db.session.add(entity)

    def delete(self, entity):
        self.db.session.delete(entity)

    def commit(self):
        self.db.session.commit()

    def rollback(self):
        self.db.session.rollback()
