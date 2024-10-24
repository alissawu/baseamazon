from flask import current_app as app
from datetime import datetime

class Seller:
    def __init__(self, acct_ID, product_ID, id, name, price, available):
        self.acct_ID = acct_ID
        self.product_ID = product_ID
        self.id = id
        self.name = name
        self.price = price
        self.available = available

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
        SELECT Seller.acct_ID, Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Products.id = Seller.product_ID
        WHERE Products.available = :available
        ''', available=available)
        return [Seller(*row) for row in rows]

    @staticmethod
    def get_products_by_seller_id(acct_ID):
        rows = app.db.execute('''
        SELECT Seller.acct_ID, Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Products.id = Seller.product_ID
        WHERE Seller.acct_ID = :acct_ID
        ''', acct_ID=acct_ID)

        return [Seller(*row) for row in rows]

    @staticmethod
    def get_all_sellers():
        rows = app.db.execute('''
        SELECT Seller.acct_ID, Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Seller.product_id = Products.id
        ''')
        return [Seller(*row) for row in rows]
