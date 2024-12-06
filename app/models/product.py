from flask import current_app as app


class Product:
    def __init__(self, id, name, price, available, category_name):
        self.id = id
        self.name = name
        self.price = price
        self.available = available
        self.category_name= category_name
    
    @classmethod
    def get_all_by_uid(cls, uid):
        return cls.query.filter_by(user_id=uid).all()

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE id = :id
''',
                              id=id)
        return Product(*rows[0]) if rows else None

    @staticmethod
    
def get_all(available=True, sort_by_price=False, sort_order='ASC'):
    query = '''
    SELECT Products.id, Products.name, Products.price, Products.available, Category.name
    FROM Products
    JOIN Category ON Category.id = Products.category_id
    WHERE available = :available
    '''
    
    # if sort_by_price is True, modify the query to include ORDER BY
    if sort_by_price:
        query += f" ORDER BY Products.price {sort_order}"

    rows = app.db.execute(query, available=available)
    
    return [Product(
        id=row[0],
        name=row[1],
        price=row[2],
        available=row[3],
        category_name=row[4]
    ) for row in rows]

    
    # Method to get the top k most expensive products
    @staticmethod
    def get_top_k_expensive(k):
        rows = app.db.execute('''
            SELECT id, name, price, available
            FROM Products
            ORDER BY price DESC
            LIMIT :k
        ''', k=k)

        # Return a list of Product objects
        return [Product(*row) for row in rows]
    
    @staticmethod
    def get_reviews(product_id, sort_by="review_date", order="desc"):
        valid_columns = ["rating_num", "review_date"]
        if sort_by not in valid_columns:
            sort_by = "review_date"  # Default column

        sort_order = "DESC" if order.lower() == "desc" else "ASC"
        
        query = f'''
            SELECT product_id, rating_num, rating_message, customer_id, review_date
            FROM UserReviewsProduct
            WHERE product_id = :product_id
            ORDER BY {sort_by} {sort_order}
        '''
        rows = app.db.execute(query, product_id=product_id)

        return [{
            'product_id': row[0],
            'rating_num': row[1],
            'rating_message': row[2],
            'customer_id': row[3],
            'review_date': row[4]
        } for row in rows]

     # Method to calculate average rating for a product
    @staticmethod
    def average_rating(product_id):
        rows = app.db.execute('''
            SELECT AVG(rating_num) 
            FROM UserReviewsProduct
            WHERE product_id = :product_id
        ''', product_id=product_id)

        return rows[0][0] if rows[0][0] is not None else 0
    
    # Method to calculate the number of reviews for a product
    @staticmethod
    def review_count(product_id):
        rows = app.db.execute('''
            SELECT COUNT(*) 
            FROM UserReviewsProduct
            WHERE product_id = :product_id
        ''', product_id=product_id)

        return rows[0][0] if rows else 0
    @staticmethod
    def can_review_product(customer_id, product_id):
        """Check if a user can review a product (i.e., if they have purchased it)."""
        rows = app.db.execute('''
            SELECT COUNT(*)
            FROM Purchases
            WHERE uid = :customer_id AND pid = :product_id
        ''', customer_id=customer_id, product_id=product_id)
        return rows[0][0] > 0



