from flask import current_app as app


class Seller:
    def __init__(self, acct_ID, product_ID, name, price, available):
        self.acct_ID = acct_ID
        self.product_ID = product_ID  # Maps to Products.id
        self.name = name
        self.price = price
        self.available = available


    # Get products for a specific seller
    @staticmethod
    def get_products_by_seller_id(acct_ID):
        rows = app.db.execute('''
        SELECT Seller.acct_ID, Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Products.id = Seller.product_ID
        WHERE Seller.acct_ID = :acct_ID
        ''', acct_ID=acct_ID)
        return [Seller(*row) for row in rows]