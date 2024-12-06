from flask import current_app as app

class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    @staticmethod
    def get_all_categories():
        rows = app.db.execute('SELECT id, name FROM Category')
        return [Category(id=row[0], name=row[1]) for row in rows]
    