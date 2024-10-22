from flask import render_template, redirect, url_for, abort, request, current_app as app
from flask_login import current_user
from decimal import Decimal
from .models.cart import Cart
from .models.order import Order
from flask import Blueprint

bp = Blueprint('sellers', __name__)

def sellers_inventory():
    return redirect(url_for('sellers.sellers_page'))
