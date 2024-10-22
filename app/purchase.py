from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from humanize import naturaltime
from app.models.purchase import Purchase  # Changed from PurchaseItem to Purchase
from datetime import datetime

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
