from flask import render_template, request, redirect, url_for
from flask_login import current_user
import datetime
from .models.product import Product
from .models.purchase import Purchase
from .models.sellers import Seller
from .models.cart import Cart

from flask import Blueprint
bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    sort_order = request.args.get('sort_order', 'ASC')  # default is 'ASC'
    available = request.args.get('available', True) # defaul is true
    products = Product.get_all(available=available, sort_by_price=True, sort_order=sort_order)

    acct_ID = request.args.get('acct_ID')
    seller_products = None

    if acct_ID:
        try:
            acct_ID = int(acct_ID.strip())
            seller_products = Seller.get_products_by_seller_id(acct_ID)
        except ValueError:
            return "Invalid Account ID. Please enter a valid integer."

    # Use the order summaries if the user is authenticated
    if current_user.is_authenticated:
        orders = Purchase.get_order_summaries_by_uid(current_user.id)
    else:
        orders = None

    cart_items = None
    if current_user.is_authenticated:
        cart_items = Cart.get_all_by_uid(current_user.id)

    return render_template(
        'index.html',
        avail_products=products,
        orders=orders,
        seller_products=seller_products,
        cart_items=cart_items
    )

@bp.route('/order/<order_id>')
def order_details(order_id):
    # Fetch all details for a particular order
    details = Purchase.get_order_details(order_id)
    return render_template('order_details.html', order_details=details)