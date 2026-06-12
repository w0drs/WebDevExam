import uuid
import os
import hashlib


class CoverService:
    def __init__(self, cover_repo, upload_folder):
        self.cover_repo = cover_repo
        self.upload_folder = upload_folder

    def save_cover(self, file, book_id):
        file_content = file.read()
        md5_hash = hashlib.md5(file_content).hexdigest()
        file.seek(0)

        existing_cover = self.cover_repo.get_by_md5(md5_hash)
        if existing_cover:
            return existing_cover

        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        filename = f"{uuid.uuid4().hex}.{ext}"

        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)

        cover = self.cover_repo.create(filename, file.mimetype, md5_hash, book_id)
        self.cover_repo.commit()

        return cover

    def delete_cover_file(self, filename):
        filepath = os.path.join(self.upload_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
