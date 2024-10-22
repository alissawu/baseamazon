from flask import current_app as app
from datetime import datetime

class Purchase:
    def __init__(self, id, uid, pid, time_purchased, product_name=None, product_price=None):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased
        self.product_name = product_name
        self.product_price = product_price

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT Purchases.id, uid, pid, time_purchased, P.name, P.price
FROM Purchases
JOIN Products P ON Purchases.pid = P.id
WHERE Purchases.uid = :uid
ORDER BY time_purchased DESC
''',
                              uid=uid)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT Purchases.id, uid, pid, time_purchased, P.name, P.price
FROM Purchases
JOIN Products P ON Purchases.pid = P.id
WHERE Purchases.uid = :uid
AND time_purchased >= :since
ORDER BY time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [Purchase(*row) for row in rows]

    @staticmethod
    def add(uid, pid):
        result = app.db.execute('''
INSERT INTO Purchases(uid, pid, time_purchased)
VALUES(:uid, :pid, :time_purchased)
RETURNING id
''',
                                uid=uid,
                                pid=pid,
                                time_purchased=datetime.now())
        id = result[0][0]
        return id

    @staticmethod
    def remove(uid, pid):
        app.db.execute('''
DELETE FROM Purchases
WHERE uid = :uid AND pid = :pid
''',
                        uid=uid,
                        pid=pid)
