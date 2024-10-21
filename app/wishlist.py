from flask import Blueprint, app, render_template, redirect, url_for
from flask_login import current_user
from humanize import naturaltime
from app.models.wishlist import WishlistItem
from datetime import datetime

bp = Blueprint('wishlist', __name__)

@bp.route('/wishlist')
def wishlist():
    if current_user.is_authenticated:
    # Get all wishlist items for the current user
        items = WishlistItem.get_all_by_uid(current_user.id)
        return render_template('wishlist.html', items=items, humanize_time=humanize_time)
    else:
        return redirect(url_for('users.login'))

@bp.route('/wishlist/add/<int:product_id>', methods=['POST'])
def wishlist_add(product_id):
    if current_user.is_authenticated:
        WishlistItem.add(current_user.id, product_id)
        return redirect(url_for('wishlist.wishlist'))
    else:
        return redirect(url_for('users.login'))
        

@bp.app_template_filter('humanize_time')
def humanize_time(dt):
    return naturaltime(datetime.now() - dt)

@bp.route('/wishlist/remove/<int:product_id>', methods=['POST'])
def wishlist_remove(product_id):
    if current_user.is_authenticated:
        WishlistItem.remove(current_user.id, product_id)
        return redirect(url_for('wishlist.wishlist'))
    else:
        return redirect(url_for('users.login'))

