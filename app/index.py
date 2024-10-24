from flask import render_template, request
from flask_login import current_user
import datetime

from .models.product import Product
from .models.purchase import Purchase
from .models.sellers import Seller  # Correctly import Seller model

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # get all available products for sale:
    products = Product.get_all(True)

    # Get the seller account ID from the query parameters
    acct_ID = request.args.get('acct_ID')
    
    # Initialize seller_products to None in case no account ID is provided
    seller_products = None

    if acct_ID:
        try:
            acct_ID = int(acct_ID.strip())  # Ensure acct_ID is an integer
            seller_products = Seller.get_products_by_seller_id(acct_ID)
        except ValueError:
            # If the provided acct_ID is invalid, handle it accordingly
            return "Invalid Account ID. Please enter a valid integer."

    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases,
                           seller_products=seller_products)
