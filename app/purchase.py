from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import current_user
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
        return redirect(url_for('purchase.purchase'))
    else:
        return redirect(url_for('users.login'))

@bp.app_template_filter('humanize_time')
def humanize_time(dt):
    return naturaltime(datetime.now() - dt)

@bp.route('/purchase/remove/<int:product_id>', methods=['POST'])
def purchase_remove(product_id):
    if current_user.is_authenticated:
        Purchase.remove(current_user.id, product_id)
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