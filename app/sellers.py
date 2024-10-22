from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from humanize import naturaltime
from app.models.purchase import Purchase  # Changed from PurchaseItem to Purchase
from datetime import datetime

bp = Blueprint('sellers', __name__)

@bp.route('/sellers')
def sellers_inventory():
    return redirect(url_for('sellers.sellers_page'))
