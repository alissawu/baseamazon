from flask import Blueprint, render_template

bp = Blueprint('product', __name__)

@bp.route('/product/<int:product_id>', methods=['GET'])
def detail(product_id):
    # Logic to fetch product details goes here
    product = product.get(product_id)
    return render_template('product_detail.html', product=product)
