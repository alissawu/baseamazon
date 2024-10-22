from flask import current_app as app


class Product:
    def __init__(self, id, name, price, available, acct_id, product_id):
        self.id = id
        self.name = name
        self.price = price
        self.available = available
        self.acct_id = acct_id
        self.product_id = product_id

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT Products.id, Products.name, Products.price, Products.available, Seller.acct_id, Seller.product_id
FROM Products
JOIN Seller ON Seller.product_id = Products.id
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
