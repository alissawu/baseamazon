-- Load Users
\COPY Users FROM 'Users.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.users_id_seq', (SELECT MAX(id)+1 FROM Users), false);

-- Load Products
\COPY Products FROM 'Products.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.products_id_seq', (SELECT MAX(id)+1 FROM Products), false);

-- Load Purchases
\COPY Purchases FROM 'Purchases.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.purchases_id_seq', (SELECT MAX(id)+1 FROM Purchases), false);

-- Load Wishes
\COPY Wishes FROM 'Wishes.csv' WITH DELIMITER ',' CSV;
SELECT pg_catalog.setval('public.wishes_id_seq', (SELECT MAX(id)+1 FROM Wishes), false);

-- Load Seller
\COPY Seller FROM 'Seller.csv' WITH DELIMITER ',' NULL '' CSV;
SELECT pg_catalog.setval('public.sellers_id_seq', (SELECT MAX(acct_ID)+1 FROM Seller), false);

-- Load UserReviewsProduct
\COPY UserReviewsProduct FROM 'UserReviewsProduct.csv' WITH DELIMITER ',' NULL '' CSV HEADER;
SELECT pg_catalog.setval('public.userreviewsproduct_id_seq', (SELECT MAX(id)+1 FROM UserReviewsProduct), false);

-- Load UserReviewsSeller
\COPY UserReviewsSeller FROM 'UserReviewsSeller.csv' WITH DELIMITER ',' NULL '' CSV HEADER;
SELECT pg_catalog.setval('public.userreviewsseller_id_seq', (SELECT MAX(id)+1 FROM UserReviewsSeller), false);
