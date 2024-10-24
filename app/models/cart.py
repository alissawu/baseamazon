from flask import current_app as app
from datetime import datetime

class Cart:
    def __init__(self, id, uid, pid, time_added, product_name=None, product_price=None):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_added = time_added
        self.product_name = product_name
        self.product_price = product_price

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_added
FROM Cart
WHERE id = :id
''',
                              id=id)
        return Cart(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT Cart.id, uid, pid, time_added, P.name, P.price
FROM Cart
JOIN Products P ON Cart.pid = P.id
WHERE Cart.uid = :uid
ORDER BY time_added DESC
''',
                              uid=uid)
        return [Cart(*row) for row in rows]

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT Cart.id, uid, pid, time_added, P.name, P.price
FROM Cart
JOIN Products P ON Cart.pid = P.id
WHERE Cart.uid = :uid
AND time_added >= :since
ORDER BY time_added DESC
''',
                              uid=uid,
                              since=since)
        return [Cart(*row) for row in rows]

    @staticmethod
    def add(uid, pid):
        result = app.db.execute('''
INSERT INTO Cart(uid, pid, time_added)
VALUES(:uid, :pid, :time_added)
RETURNING id
''',
                                uid=uid,
                                pid=pid,
                                time_added=datetime.now())
        id = result[0][0]
        return id

    @staticmethod
    def remove(uid, pid):
        app.db.execute('''
DELETE FROM Cart
WHERE uid = :uid AND pid = :pid
''',
                        uid=uid,
                        pid=pid)
