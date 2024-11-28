CREATE EXTENSION IF NOT EXISTS cube CASCADE;
CREATE EXTENSION IF NOT EXISTS earthdistance CASCADE;

-- Users table
CREATE TABLE public.users (
    user_id bigint GENERATED BY DEFAULT AS IDENTITY NOT NULL,
    name text NOT NULL,
    location text DEFAULT 'Calpoly SLO'::text,
    longitude double precision DEFAULT 120.6625,
    latitude double precision DEFAULT 35.3050,
    CONSTRAINT User_pkey PRIMARY KEY (user_id),
    CONSTRAINT users_username_key UNIQUE (name)
);

-- Stores table
CREATE TABLE public.store (
    store_id integer GENERATED BY DEFAULT AS IDENTITY NOT NULL,
    name text,
    catalog_id integer,
    latitude double precision,
    longitude double precision,
    open_time timestamp without time zone,
    close_time timestamp without time zone,
    CONSTRAINT store_pkey PRIMARY KEY (store_id)
);

INSERT INTO store(name, catalog_id, latitude, longitude, open_time, close_time)
VALUES ('Trader Joes', 1, 150, 150, '2024-10-28 08:30:00', '2024-10-30 09:00:00'),
('Campus Market', 2, 150, 150, '2024-10-25 08:00:00', '2024-10-30 21:00:00');

-- Food items table
CREATE TABLE public.food_item (
    food_id bigint generated by default as identity not null,
    name text null,
    serving_size text null,
    calories integer null,
    saturated_fat integer null,
    trans_fat integer null,
    dietary_fiber integer null,
    total_carbohydrate integer null,
    total_sugars integer null,
    protein integer null,
    CONSTRAINT food_item_pkey PRIMARY KEY (food_id)
  );

  INSERT INTO food_item(name, serving_size, calories, saturated_fat, trans_fat, dietary_fiber, total_carbohydrate, total_sugars, protein)
  VALUES ('Grilled Chicken', 4, 200, 15, 5, 0, 0, 0, 30),
  ('Oreos', 8, 1000, 200, 250, 0, 0, 190, 0);

-- Catalog table (allows stores to have multiple catalogs)
CREATE TABLE public.catalog (
    catalog_id integer generated by default as identity not null,
    store_id integer null,
    CONSTRAINT catalog_pkey PRIMARY KEY (catalog_id)
  );

INSERT INTO catalog(catalog_id, store_id)
VALUES (1, 1),
(2, 2);

-- Catalog Items table (joins specific catalogs with food items and their associated prices)
CREATE TABLE public.catalog_item (
    catalog_item_id integer generated by default as identity not null,
    catalog_id integer null,
    food_id integer null,
    price integer null,
    quantity integer null,
    CONSTRAINT catalog_item_pkey PRIMARY KEY (catalog_item_id),
    CONSTRAINT catalog_item_catalog_id_fkey FOREIGN KEY (catalog_id) REFERENCES catalog (catalog_id),
    CONSTRAINT catalog_item_food_id_fkey FOREIGN KEY (food_id) REFERENCES food_item (food_id)
  );

  INSERT INTO catalog_item(catalog_id, food_id, price, quantity)
  VALUES(1, 1, 1099, 12),
  (2, 1, 1000099, 2),
  (2, 2, 1799, 15);

CREATE TABLE public.shopping_list (
    list_id integer GENERATED BY DEFAULT AS IDENTITY NOT NULL,
    name text,
    user_id bigint,
    CONSTRAINT shopping_list_pkey PRIMARY KEY (list_id),
    CONSTRAINT shopping_list_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE public.shopping_list_item (
    list_id integer NOT NULL,
    food_id integer NOT NULL,
    user_id bigint NOT NULL,
    quantity integer,
    CONSTRAINT shopping_list_item_pkey PRIMARY KEY (list_id, food_id),
    CONSTRAINT shopping_list_item_food_id_fkey FOREIGN KEY (food_id) REFERENCES food_item(food_id),
    CONSTRAINT shopping_list_item_list_id_fkey FOREIGN KEY (list_id) REFERENCES shopping_list(list_id),
    CONSTRAINT shopping_list_item_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id)
);
