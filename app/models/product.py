from flask import current_app as app


class Product:
    def __init__(self, id, name, price, available):
        self.id = id
        self.name = name
        self.price = price
        self.available = available
    
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
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT id, name, price, available
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
    
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
    def get_reviews(product_id):
        rows = app.db.execute('''
            SELECT product_id, rating_num, rating_message, customer_id, review_date
            FROM UserReviewsProduct
            WHERE product_id = :product_id
            ORDER BY review_date DESC
        ''', product_id=product_id)

        return [{
            'product_id': row[0],  # Ensure product_id is the first column in SELECT
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


