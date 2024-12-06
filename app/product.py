from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user
from app.models.product import Product 
from flask import current_app as app

bp = Blueprint('product', __name__)

@bp.route('/product/<int:product_id>', methods=['GET'])
def detail(product_id):
    product = Product.get(product_id)
    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for('index.index'))

    sort_by = request.args.get("sort_by", "review_date")  # Default: review_date
    order = request.args.get("order", "desc")  # Default: descending

    reviews = Product.get_reviews(product_id, sort_by=sort_by, order=order)
    avg_rating = Product.average_rating(product_id)
    review_count = Product.review_count(product_id)

    return render_template(
        'product.html', 
        product=product, 
        reviews=reviews, 
        avg_rating=avg_rating, 
        review_count=review_count,
        sort_by=sort_by,
        order=order
    )


# Route to handle listing of top k products
@bp.route('/product', methods=['GET', 'POST'])
def products():
    # Default value of k
    k = request.form.get('k', 5)  # Get the value of k from the form, default to 5 if not provided

    # Handle form submission (when k is provided)
    if request.method == 'POST':
        try:
            # Convert k to integer
            k = int(k)
        except ValueError:
            k = 5  # Default to 5 if invalid input

    # Query to find the top k most expensive products
    top_products_query = '''
        SELECT product_ID, name, price, description, category, image
        FROM Products
        ORDER BY price DESC
        LIMIT :k
    '''
    # Execute the query with the provided k
    products = app.db.execute(top_products_query, k=k)

    # Render the template and pass the products and k value
    return render_template('product.html', products=products, k=k)

@bp.route('/product/top_k', methods=['GET'])
def get_top_k_expensive():
    # Get the value of 'k' from the form query parameters
    k = request.args.get('k')

    # Handle the case where 'k' is not provided or invalid
    if not k:
        return "Please provide a valid value for 'k'.", 400

    try:
        k = int(k)  # Convert the input to an integer
    except ValueError:
        return "Invalid value for 'k'. Please enter a valid integer.", 400

    # Fetch the top k most expensive products using the model
    top_products = Product.get_top_k_expensive(k)

    # Render the template and pass the top products to display
    return render_template('product.html', products=top_products)