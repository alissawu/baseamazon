from flask import Blueprint, render_template, redirect, url_for
from flask import current_app as app
from flask_login import current_user
from humanize import naturaltime
from app.models.purchase import Purchase  # Changed from PurchaseItem to Purchase
from datetime import datetime

bp = Blueprint('sellers', __name__)

@bp.route('/sellers')
def sellers_inventory():
    products = Seller.get_products_by_seller(acct_id)
    return render_template('sellers.html')

class Seller:
     def __init__(self, id, name, price, available):
        self.id = id
        self.name = name
        self.price = price
        self.available = available

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
SELECT id, name, price, available
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
    '''
    def __init__(self, acct_id, product_id, product_name):
        self.acct_id = acct_id
        self.product_id = product_id
        # self.product_name = product_name
    
    @staticmethod
    def get_products_by_seller(acct_id):
        rows = app.db.execute(
        SELECT Products.id, Products.name, Products.price
        FROM Sellers
        JOIN Products ON Sellers.product_id = Products.id
        WHERE Sellers.acct_id = :acct_id
        , acct_id=acct_id)

        return [Product(*row) for row in rows]

    '''