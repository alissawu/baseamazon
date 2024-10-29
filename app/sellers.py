from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user
from flask import current_app as app
from .models.sellers import Seller

bp = Blueprint('sellers', __name__)



# get a seller's inventory by their ID
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

# display products not in seller's inventory
@bp.route('/sellers/not_inventory', methods=['GET'])
def seller_not_inventory():
    acct_ID = request.args.get('acct_ID')
    if acct_ID and current_user.is_authenticated:
        products = Seller.get_products_not_in_inventory(acct_ID)
        return render_template('sellers_add.html', products=products)
    else:
        return redirect(url_for('users.login'))

# add a product to the seller's inventory
@bp.route('/sellers/add_product/<int:product_id>/<int:acct_ID>', methods=['POST'])
def add_product_to_inventory(product_id, acct_ID):
    if current_user.is_authenticated:
        Seller.add_product_to_inventory(acct_ID, product_id)
        flash("Product added to inventory successfully.")
        return redirect(url_for('sellers.get_seller_products', acct_ID=acct_ID))
    else:
        return redirect(url_for('users.login'))

