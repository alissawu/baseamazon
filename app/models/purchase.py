from flask import current_app as app
from datetime import datetime

class Purchase:
    def __init__(self, id, uid, pid, order_id, time_purchased, product_name=None, product_price=None):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.order_id = order_id
        self.time_purchased = time_purchased
        self.product_name = product_name
        self.product_price = product_price
    
    @staticmethod
    def get_order_summaries_by_uid(uid):
        """
        Fetch order summaries for a given user ID (uid).
        Each summary contains:
        - order_id: Unique identifier for the order.
        - purchase_time: Earliest purchase time in the order.
        - total_cost: Total price of all items in the order.
        - total_items: Total number of items in the order.
        """
        rows = app.db.execute('''
            SELECT order_id,
                   MIN(time_purchased) AS purchase_time,
                   SUM(P.price) AS total_cost,
                   COUNT(*) AS total_items
            FROM Purchases
            JOIN Products P ON Purchases.pid = P.id
            WHERE Purchases.uid = :uid
            GROUP BY order_id
            ORDER BY purchase_time DESC
        ''', uid=uid)

        # Convert rows to a list of dictionaries for easier use in templates
        return [
            {
                "order_id": row[0],
                "purchase_time": row[1],
                "total_cost": row[2],
                "total_items": row[3]
            }
            for row in rows
        ]
    
    @staticmethod
    def get_order_details(order_id):
        rows = app.db.execute('''
            SELECT Purchases.id,
                P.name,
                P.price,
                Purchases.time_purchased
            FROM Purchases
            JOIN Products P ON Purchases.pid = P.id
            WHERE order_id = :order_id
            ORDER BY time_purchased
        ''', order_id=order_id)
        return rows

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid,order_id, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT Purchases.id, uid, pid, order_id, time_purchased, P.name, P.price
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
SELECT Purchases.id, uid, pid, order_id, time_purchased, P.name, P.price
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
    def add(uid, order_id, pid):
        result = app.db.execute('''
INSERT INTO Purchases(uid, pid, order_id, time_purchased)
VALUES(:uid, :pid, :order_id, :time_purchased)
RETURNING id
''',
                                uid=uid,
                                pid=pid,
                                order_id=order_id,
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
    @classmethod
    def get_by_id(cls, id):
        purchase = app.db.execute('''
            SELECT * FROM Purchases WHERE id = :id
        ''', id=id)

        return purchase[0] if purchase else None  # Return the first result or None

    @classmethod
    def remove_by_id(cls, id):
        app.db.execute('''
            DELETE FROM Purchases WHERE id = :id
        ''', id=id)
