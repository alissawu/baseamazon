from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from flask import current_app as app
from .models.sellers import Seller

bp = Blueprint('sellers', __name__)



# Route for getting a seller's inventory by their ID
@bp.route('/sellers/user', methods=['GET'])
def get_seller_products():
    acct_ID = request.args.get('acct_ID')
    print(f"Received acct_ID: '{acct_ID}'")  # Debugging print

    if acct_ID:
        try:
            acct_ID = int(acct_ID.strip())
        except ValueError:
            return "Invalid Account ID"
    else:
        return "Enter a valid Account ID"

    products = Seller.get_products_by_seller_id(acct_ID)
    
    if not products:
        return "No products found for this seller."
    
    return render_template('sellers.html', products=products)
