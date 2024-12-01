from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user
from flask import current_app as app
from .models.sellers import Seller
from flask import session
from decimal import Decimal, InvalidOperation

bp = Blueprint('sellers', __name__)

# get a seller's inventory by their ID
@bp.route('/sellers/user', methods=['GET'])
def get_seller_products():
    acct_ID = request.args.get('acct_ID')
    print(f"Received acct_ID: '{acct_ID}'")

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
    print(f"Received acct_ID in seller_not_inventory: '{acct_ID}'")  # Debugging print

    if acct_ID:
        try:
            acct_ID = int(acct_ID.strip())
        except ValueError:
            return "Invalid Account ID"

        products = Seller.get_products_not_in_inventory(acct_ID)
        for product in products:
            print(f"Add Product - Product ID: {product.product_ID}, Product Name: {product.name}")
        return render_template('sellers_add.html', products=products)
    return "Enter a valid Account ID"

# add a product to the seller's inventory
@bp.route('/sellers/add_product/<int:product_id>', methods=['POST'])
def add_product_to_inventory(product_id):
    acct_ID = request.args.get('acct_ID')
    if acct_ID and current_user.is_authenticated:
        try:
            acct_ID = int(acct_ID.strip())
            Seller.add_product_to_inventory(acct_ID, product_id)
        except ValueError:
            return "Invalid Account ID"
    products = Seller.get_products_by_seller_id(acct_ID)
    return render_template('sellers.html', products=products, acct_ID=acct_ID)

# remove a product to the seller's inventory
@bp.route('/sellers/remove_product/<int:product_id>', methods=['POST'])
def remove_product_from_inventory(product_id):
    acct_ID = request.args.get('acct_ID')
    if acct_ID and current_user.is_authenticated:
        try:
            acct_ID = int(acct_ID.strip())
            Seller.remove_product_from_inventory(acct_ID, product_id)
        except ValueError:
            return "Invalid Account ID"
    # get the updated list of products in the seller's inventory
    products = Seller.get_products_by_seller_id(acct_ID)
    return render_template('sellers.html', products=products, acct_ID=acct_ID)

# update the quantity of a product in the seller's inventory
@bp.route('/seller/update_quantity/<int:product_id>/<int:acct_ID>', methods=['POST'])
def update_quantity(product_id, acct_ID):
    current_quantity = int(request.form['quantity'])
    change = int(request.form['change'])
    new_quantity = current_quantity + change
    if new_quantity < 0:
        new_quantity = 0
    Seller.update_quantity_in_inventory(acct_ID, product_id, new_quantity)
    return redirect(url_for('sellers.get_seller_products', acct_ID=acct_ID))

@bp.route('/sellers/product', methods=['GET', 'POST'])
def add_products():
    
    acct_ID = request.args.get('acct_ID') or request.form.get('acct_ID')
    
    if request.method == 'POST':
        # get form values
        product_ID = request.form.get('product_ID') or request.args.get('product_ID')
        name = request.form.get('name') or request.args.get('name')
        price = request.form.get('price') or request.args.get('price')
        available = request.form.get('available') or request.args.get('available')
        quantity = request.form.get('quantity') or request.args.get('quantity')
        
        # check if price is a decimal
        try:
            price = Decimal(price)
        except InvalidOperation:
            return redirect(url_for('sellers.add_products', acct_ID=acct_ID))

        # check if 'available' is either 'True' or 'False'
        if available not in ['True', 'False']:
            return redirect(url_for('sellers.add_products', acct_ID=acct_ID))
        
        # add product to the database
        success = Seller.add_product_to_database(acct_ID, product_ID, name, price, available, quantity)

        if success:
            # get the updated list of products for the seller
            products = Seller.get_products_by_seller_id(acct_ID)
            return render_template('sellers.html', products=products, acct_ID=acct_ID)
        else:
            return redirect(url_for('sellers.add_products', acct_ID=acct_ID))

    # if GET request, fetch and display the list of products
    products = Seller.get_products_by_seller_id(acct_ID)
    return render_template('sellers.html', products=products, acct_ID=acct_ID)