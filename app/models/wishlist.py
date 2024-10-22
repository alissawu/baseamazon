from flask import current_app as app

class WishlistItem:
    def __init__(self, id, uid, pid, time_added, product_name, product_price):
        self.id = id
        self.uid = uid  
        self.pid = pid  
        self.time_added = time_added  
        self.product_name = product_name
        self.product_price = product_price
    # fetches specific wishlist item from db by ID
    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return WishlistItem(*(rows[0])) if rows else None
    
    # retrieves all wishlist items for user
    @staticmethod
    def get_all_by_uid(uid):
        rows = app.db.execute('''
SELECT W.id, W.uid, W.pid, W.time_added, P.name, P.price
FROM Wishes W
JOIN Products P ON W.pid = P.id
WHERE W.uid = :uid
ORDER BY W.time_added DESC
''', uid=uid)
        return [WishlistItem(*row) for row in rows]

    
    @staticmethod
    def add(uid, pid):
        try:
            rows = app.db.execute('''
INSERT INTO Wishes (uid, pid, time_added)
VALUES (:uid, :pid, current_timestamp)
RETURNING id
''', uid=uid, pid=pid)
            return rows[0][0]  
        except Exception as e:
            print(str(e))
            return None
#do later
    @staticmethod
    def remove(uid, product_id):
        try:
            app.db.execute('''
DELETE FROM Wishes
WHERE uid = :uid AND pid = :product_id
''', uid=uid, product_id=product_id)
        except Exception as e:
            print(str(e))
