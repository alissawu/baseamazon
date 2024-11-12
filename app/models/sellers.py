from flask import current_app as app


class Seller:
    def __init__(self, acct_ID=None, product_ID=None, name=None, price=None, available=None):
        self.acct_ID = acct_ID
        self.product_ID = product_ID
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

    # Get products not in a seller's inventory
    @staticmethod
    def get_products_not_in_inventory(acct_ID):
        rows = app.db.execute('''
        SELECT Products.id, Products.name, Products.price, Products.available
        FROM Products
        WHERE Products.id NOT IN (
            SELECT product_ID
            FROM Seller
            WHERE acct_ID = :acct_ID
            )
            ''', acct_ID=acct_ID)
        return [Seller(*row) for row in rows]

    # Add a product to the seller's inventory
    @staticmethod
    def add_product_to_inventory(acct_ID, product_ID):
        app.db.execute('''
        INSERT INTO Seller (acct_ID, product_ID)
        VALUES (:acct_ID, :product_ID)
        ''', acct_ID=acct_ID, product_ID=product_ID)
