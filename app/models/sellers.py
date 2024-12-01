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
        app.db.execute('''
        UPDATE Seller
        SET quantity = :new_quantity
        WHERE acct_ID = :acct_ID AND product_ID = :product_ID
        ''', acct_ID=acct_ID, product_ID=product_ID, new_quantity=new_quantity)

    # add a product to the database
    @staticmethod
    def add_product_to_database(acct_ID, product_ID, name, price, available, quantity):
        # check if the product ID or product name are already in the database
        existing_product = app.db.execute('''
            SELECT * FROM Products WHERE id = :product_ID OR name = :name
        ''', product_ID=product_ID, name=name)

        # raise an error if so, proceed if not
        if existing_product:
            flash("Product found with the given ID or name.")
            return False

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