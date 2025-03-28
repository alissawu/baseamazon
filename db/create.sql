-- Feel free to modify this file to match your development goal.
-- Here we only create 3 tables for demo purpose.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE Users (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    account_balance DECIMAL(12, 2) NOT NULL DEFAULT 0.00
);

-- category
CREATE TABLE Category (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Products (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    name VARCHAR(255) UNIQUE NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    category_id INT NOT NULL
);

CREATE TABLE Purchases (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

CREATE TABLE Wishes (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    time_added timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

/* MILESTONE 3 */
CREATE TABLE UserReviewsProduct (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    customer_id INT NOT NULL REFERENCES Users(id),
    product_id INT NOT NULL REFERENCES Products(id),
    rating_num INT CHECK (rating_num >= 1 AND rating_num <= 5), -- rating between 1 and 5
    rating_message TEXT,
    review_date TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    UNIQUE (customer_id, product_id) -- Unique constraint for one review per user per product
);


CREATE TABLE UserReviewsSeller (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    customer_id INT NOT NULL REFERENCES Users(id),
    seller_id INT NOT NULL REFERENCES Users(id), -- assuming sellers are users
    rating_num INT CHECK (rating_num >= 1 AND rating_num <= 5), -- rating between 1 and 5
    rating_message TEXT,
    review_date TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC'),
    UNIQUE (customer_id, seller_id) -- Unique constraint for one review per user per seller
);

CREATE TABLE Messages (
    msg_num SERIAL PRIMARY KEY,  -- Unique message ID
    customer_ID INT REFERENCES Users(id),  -- User who sent the message
    seller_ID INT REFERENCES Users(id),  -- Seller who received the message
    product_ID INT REFERENCES Products(id),  -- Product related to the message
    message TEXT NOT NULL,  -- The actual message
    message_date TIMESTAMP DEFAULT current_timestamp  -- Date of the message
);


-- Table for Seller
CREATE TABLE Seller (
    acct_ID INT NOT NULL,
    product_ID INT NOT NULL,
    quantity INT DEFAULT 0,
    PRIMARY KEY (acct_ID, product_ID),
    FOREIGN KEY (acct_ID) REFERENCES Users(id),
    FOREIGN KEY (product_ID) REFERENCES Products(id)
);

-- Table for Inventory
CREATE TABLE Inventory (
    acct_ID INT NOT NULL,
    product_ID INT NOT NULL,
    available_quantity INT DEFAULT 0,
    PRIMARY KEY (acct_ID, product_ID),
    FOREIGN KEY (acct_ID) REFERENCES Users(id),
    FOREIGN KEY (product_ID) REFERENCES Products(id)
);

-- Table for Cart
CREATE TABLE Cart (
    id INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    uid INT NOT NULL REFERENCES Users(id),
    pid INT NOT NULL REFERENCES Products(id),
    time_added timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

-- Table for Orders
CREATE TABLE Orders (
    order_ID INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    acct_ID INT NOT NULL REFERENCES Users(id),
    total_cost DECIMAL(12, 2) DEFAULT 0.00,
    order_date TIMESTAMP WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    order_status VARCHAR(50) DEFAULT 'Pending'
);

-- Table for OrderItem
CREATE TABLE OrderItem (
    order_item_ID INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    order_ID INT NOT NULL REFERENCES Orders(order_ID),
    product_ID INT NOT NULL REFERENCES Products(id),
    order_item_status VARCHAR(50) DEFAULT 'Processing'
);

-- Table for UserSendsMessage
CREATE TABLE UserSendsMessage (
    customer_ID INT NOT NULL REFERENCES Users(id),
    product_ID INT,
    seller_ID INT NOT NULL,
    FOREIGN KEY (seller_ID, product_ID) REFERENCES Seller(acct_ID, product_ID),
    PRIMARY KEY (customer_ID, seller_ID)
);

-- Table for Message
CREATE TABLE Message (
    msg_num INT NOT NULL PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    customer_ID INT NOT NULL REFERENCES Users(id),
    message TEXT NOT NULL,
    message_date TIMESTAMP WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    product INT REFERENCES Products(id)
);
