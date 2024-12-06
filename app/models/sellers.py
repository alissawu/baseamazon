from flask import current_app as app
from flask import flash


class Seller:
    def __init__(self, acct_ID=None, product_ID=None, name=None, price=None, available=None, quantity=None):
        self.acct_ID = acct_ID
        self.product_ID = product_ID
        self.name = name
        self.price = price
        self.available = available
        self.quantity = quantity

    @staticmethod
    def get(acct_ID):
        rows = app.db.execute('''
        SELECT *
        FROM seller
        WHERE acct_ID = :acct_ID
        ''', acct_ID=acct_ID)
        return Seller(*rows[0]) if rows else None
    
    @staticmethod
    def get_recent_sales_by_seller_id(acct_ID):
        rows = app.db.execute('''
            SELECT Purchases.order_id,
                COUNT(*) AS total_quantity,
                MIN(Purchases.time_purchased) AS sale_date,
                SUM(Products.price) AS total_price
            FROM Purchases
            JOIN Seller ON Purchases.pid = Seller.product_ID
            JOIN Products ON Products.id = Seller.product_ID
            WHERE Seller.acct_ID = :acct_ID
            GROUP BY Purchases.order_id
            ORDER BY sale_date DESC
        ''', acct_ID=acct_ID)
        
        return [{
            'order_id': row[0],
            'total_quantity': row[1],
            'sale_date': row[2],
            'total_price': row[3]
        } for row in rows]

    # get products for a specific seller
    @staticmethod
    def get_products_by_seller_id(acct_ID):
        rows = app.db.execute('''
        SELECT Seller.acct_ID, Products.id, Products.name, Products.price, Products.available, Seller.quantity
        FROM Seller
        JOIN Products ON Products.id = Seller.product_ID
        WHERE Seller.acct_ID = :acct_ID
        ''', acct_ID=acct_ID)
        print(rows)
        return [Seller(*row) for row in rows]

    # get products not in a seller's inventory
    @staticmethod
    def get_products_not_in_inventory(acct_ID):
        rows = app.db.execute('''
        SELECT Products.id, Products.name, Products.price, Products.available
        FROM Products
        WHERE Products.id NOT IN (
            SELECT product_ID
            FROM Seller
            WHERE acct_ID = :acct_ID
            )
            ''', acct_ID=acct_ID)
        print("Query Result Rows:", rows)
        return [Seller(
            product_ID=int(row[0]),
            name=str(row[1]),
            price=float(row[2]),
            available=bool(row[3])
            ) for row in rows]

    # add a product to the seller's inventory
    @staticmethod
    def add_product_to_inventory(acct_ID, product_ID):
        app.db.execute('''
        INSERT INTO Seller (acct_ID, product_ID)
        VALUES (:acct_ID, :product_ID)
        ''', acct_ID=acct_ID, product_ID=product_ID)

    # remove a product from a seller's inventory
    @staticmethod
    def remove_product_from_inventory(acct_ID, product_ID):
        app.db.execute('''
        DELETE FROM Seller
        WHERE acct_ID = :acct_ID AND product_ID = :product_ID
        ''', acct_ID=acct_ID, product_ID=product_ID)

    # update the quantity of a product in inventory
    @staticmethod
    def update_quantity_in_inventory(acct_ID, product_ID, new_quantity):
        if new_quantity > 0:
            available = True
        else:
            available = False
        app.db.execute('''
        UPDATE Seller
        SET quantity = :new_quantity
        WHERE acct_ID = :acct_ID AND product_ID = :product_ID
        ''', acct_ID=acct_ID, product_ID=product_ID, new_quantity=new_quantity)             
        
        app.db.execute('''
        UPDATE Products
        SET available = :available
        WHERE id = :product_ID
        ''', product_ID=product_ID, available=available)

    # add a product to the database
    @staticmethod
    def add_product_to_database(acct_ID, product_ID, name, price, available, quantity):
        # check if the product ID or product name are already in the database
        existing_product = app.db.execute('''
            SELECT * FROM Products WHERE id = :product_ID OR name = :name
        ''', product_ID=product_ID, name=name)

        # raise an error if so, proceed if not
        if existing_product:
            return "Product found with the given ID or name."

        # insert into product table
        app.db.execute('''
        INSERT INTO Products (id, name, price, available)
        VALUES (:product_ID, :name, :price, :available)
        ON CONFLICT (id) DO NOTHING
        ''', product_ID=product_ID, name=name, price=price, available=available)

        # insert into Seller table
        app.db.execute('''
        INSERT INTO Seller (acct_ID, product_ID, quantity)
        VALUES (:acct_ID, :product_ID, :quantity)
        ''', acct_ID=acct_ID, product_ID=product_ID, quantity=quantity)
    @staticmethod
    def get_reviews(seller_id):
        """Retrieve all reviews for a seller, ordered by review_date descending."""
        rows = app.db.execute('''
            SELECT id, seller_id, rating_num, rating_message, customer_id, review_date
            FROM UserReviewsSeller
            WHERE seller_id = :seller_id
            ORDER BY review_date DESC
        ''', seller_id=seller_id)

        return [{
            'id': row[0],
            'seller_id': row[1],
            'rating_num': row[2],
            'rating_message': row[3],
            'customer_id': row[4],
            'review_date': row[5]
        } for row in rows]


    @staticmethod
    def average_rating(seller_id):
        """Calculate the average rating for a seller."""
        rows = app.db.execute('''
            SELECT AVG(rating_num)
            FROM UserReviewsSeller
            WHERE seller_id = :seller_id
        ''', seller_id=seller_id)
        return rows[0][0] if rows[0][0] is not None else 0

    @staticmethod
    def review_count(seller_id):
        """Count the number of reviews for a seller."""
        rows = app.db.execute('''
            SELECT COUNT(*)
            FROM UserReviewsSeller
            WHERE seller_id = :seller_id
        ''', seller_id=seller_id)
        return rows[0][0] if rows else 0

    @staticmethod
    def add_review(customer_id, seller_id, rating_num, rating_message):
        """Add or update a review for a seller."""
        existing_review = app.db.execute('''
            SELECT id
            FROM UserReviewsSeller
            WHERE customer_id = :customer_id AND seller_id = :seller_id
        ''', customer_id=customer_id, seller_id=seller_id)

        if existing_review:
            app.db.execute('''
                UPDATE UserReviewsSeller
                SET rating_num = :rating_num, rating_message = :rating_message, review_date = current_timestamp
                WHERE customer_id = :customer_id AND seller_id = :seller_id
            ''', customer_id=customer_id, seller_id=seller_id, rating_num=rating_num, rating_message=rating_message)
        else:
            app.db.execute('''
                INSERT INTO UserReviewsSeller (customer_id, seller_id, rating_num, rating_message, review_date)
                VALUES (:customer_id, :seller_id, :rating_num, :rating_message, current_timestamp)
            ''', customer_id=customer_id, seller_id=seller_id, rating_num=rating_num, rating_message=rating_message)

    @staticmethod
    def delete_review(customer_id, seller_id):
        """Delete a review for a seller."""
        app.db.execute('''
            DELETE FROM UserReviewsSeller
            WHERE customer_id = :customer_id AND seller_id = :seller_id
        ''', customer_id=customer_id, seller_id=seller_id)

    @staticmethod
    def can_review_seller(customer_id, seller_id):
        """Check if a user can review a seller (i.e., if they have purchased from them)."""
        rows = app.db.execute('''
            SELECT COUNT(*)
            FROM Purchases
            JOIN Seller ON Purchases.pid = Seller.product_ID
            WHERE Purchases.uid = :customer_id AND Seller.acct_ID = :seller_id
        ''', customer_id=customer_id, seller_id=seller_id)
        return rows[0][0] > 0  # Returns True if the count is > 0


    