from flask import current_app as app


class Seller:
    def __init__(self, acct_ID=None, product_ID=None, name=None, price=None, available=None, quantity=None):
        self.acct_ID = acct_ID
        self.product_ID = product_ID
        self.name = name
        self.price = price
        self.available = available
        self.quantity = quantity


    # Get products for a specific seller
    @staticmethod
    def get_products_by_seller_id(acct_ID):
        rows = app.db.execute('''
        SELECT Seller.acct_ID, Products.id, Products.name, Products.price, Products.available
        FROM Seller
        JOIN Products ON Products.id = Seller.product_ID
        WHERE Seller.acct_ID = :acct_ID
        ''', acct_ID=acct_ID)
        return [Seller(*row) for row in rows]

    # Get products not in a seller's inventory
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
        print("Query Result Rows:", rows)  # Debugging: Print rows to verify column order
        return [Seller(
            product_ID=int(row[0]),  # Ensure Product ID is an integer
            name=str(row[1]),        # Ensure Product Name is a string
            price=float(row[2]),     # Ensure Product Price is a float
            available=bool(row[3])
            ) for row in rows]

    # Add a product to the seller's inventory
    @staticmethod
    def add_product_to_inventory(acct_ID, product_ID):
        app.db.execute('''
        INSERT INTO Seller (acct_ID, product_ID)
        VALUES (:acct_ID, :product_ID)
        ''', acct_ID=acct_ID, product_ID=product_ID)

    # Remove a product from a seller's inventory
    @staticmethod
    def remove_product_from_inventory(acct_ID, product_ID):
        app.db.execute('''
        DELETE FROM Seller
        WHERE acct_ID = :acct_ID AND product_ID = :product_ID
        ''', acct_ID=acct_ID, product_ID=product_ID)
    # 
    @staticmethod
    def remove_product_from_inventory(acct_ID, product_ID):
        app.db.execute('''
        DELETE FROM Seller
        WHERE acct_ID = :acct_ID AND product_ID = :product_ID
        ''', acct_ID=acct_ID, product_ID=product_ID)
