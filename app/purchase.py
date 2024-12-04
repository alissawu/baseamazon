from flask import Blueprint, render_template, redirect, url_for, request, jsonify, flash
from flask_login import current_user
from flask import current_app as app
from app.models.purchase import Purchase  # Changed from PurchaseItem to Purchase
from datetime import datetime
from humanize import naturaltime

bp = Blueprint('purchase', __name__)

@bp.route('/purchase')
def purchase():
    if current_user.is_authenticated:
        # Get all purchase items for the current user
        items = Purchase.get_all_by_uid(current_user.id)
        return render_template('purchase.html', items=items, humanize_time=humanize_time)
    else:
        return redirect(url_for('users.login'))

@bp.route('/purchase/add/<int:product_id>', methods=['POST'])
def purchase_add(product_id):
    if current_user.is_authenticated:
        Purchase.add(current_user.id, product_id)
        
        # update product quantity
        product = app.db.execute('''
            SELECT Products.*, Seller.quantity
            FROM Products
            JOIN Seller ON Seller.product_ID = Products.id
            WHERE Products.id = :product_id
        ''', product_id=product_id)

        if not product:
            flash("Product not found.")
            return redirect(url_for('purchase.purchase'))

        # decrease quantity by 1 for the purchased product
        new_quantity = product[0][4] - 1
        
        if new_quantity >= 0:
            app.db.execute('''
                UPDATE Seller SET quantity = :quantity WHERE product_ID = :product_id
            ''', quantity=new_quantity, product_id=product_id)
        else:
            return "Insufficient quantity available."
        
        return redirect(url_for('purchase.purchase'))
    else:
        return redirect(url_for('users.login'))

@bp.app_template_filter('humanize_time')
def humanize_time(dt):
    return naturaltime(datetime.now() - dt)

@bp.route('/purchase/remove/<int:purchase_id>', methods=['POST'])
def purchase_remove(purchase_id):
    if current_user.is_authenticated:
        # Fetch the purchase instance by ID
        purchase = Purchase.get_by_id(purchase_id)
        if not purchase or purchase.uid != current_user.id:
            flash("Purchase not found or unauthorized action.")
            return redirect(url_for('purchase.purchase'))

        # Remove the purchase instance
        Purchase.remove_by_id(purchase_id)

        # Update product quantity
        product = app.db.execute('''
            SELECT Products.*, Seller.quantity
            FROM Products
            JOIN Seller ON Seller.product_ID = Products.id
            WHERE Products.id = :product_id
        ''', product_id=purchase.pid)

        if not product:
            flash("Product not found.")
            return redirect(url_for('purchase.purchase'))

        # Increase quantity by 1 for the removed purchase
        new_quantity = product[0][4] + 1
        app.db.execute('''
            UPDATE Seller SET quantity = :quantity WHERE product_ID = :product_id
        ''', quantity=new_quantity, product_id=purchase.pid)

        return redirect(url_for('purchase.purchase'))
    else:
        return redirect(url_for('users.login'))

@bp.route('/purchase/user', methods=['GET'])
def get_purchases_by_uid():
    if current_user.is_authenticated:
        # Get the user ID from the request
        uid = request.args.get('acct_ID')
        if uid is None:
            return jsonify({'error': 'User ID not provided'}), 400
        
        # Fetch all purchases by the specified user ID (uid)
        items = Purchase.get_all_by_uid(uid)
        if not items:
            return jsonify({'error': 'No purchases found for this user.'}), 404
        return render_template('purchase.html', items=items, humanize_time=humanize_time)
    else:
        return redirect(url_for('users.login'))