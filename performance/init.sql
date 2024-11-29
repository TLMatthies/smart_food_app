DROP EXTENSION IF EXISTS cube CASCADE;
DROP EXTENSION IF EXISTS earthdistance CASCADE;

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

-- Food items table
CREATE TABLE public.food_item (
    food_id bigint generated by default as identity not null,
    name text null,
    serving_size int null,
    calories integer null,
    saturated_fat integer null,
    trans_fat integer null,
    dietary_fiber integer null,
    total_carbohydrate integer null,
    total_sugars integer null,
    protein integer null,
    CONSTRAINT food_item_pkey PRIMARY KEY (food_id)
);

-- Catalog table
CREATE TABLE public.catalog (
    catalog_id integer generated by default as identity not null,
    store_id integer null,
    CONSTRAINT catalog_pkey PRIMARY KEY (catalog_id)
);

-- Catalog Items table
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
    CONSTRAINT unique_user_list_item UNIQUE (user_id, list_id, food_id),
    CONSTRAINT shopping_list_item_food_id_fkey FOREIGN KEY (food_id) REFERENCES food_item(food_id),
    CONSTRAINT shopping_list_item_list_id_fkey FOREIGN KEY (list_id) REFERENCES shopping_list(list_id),
    CONSTRAINT shopping_list_item_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(user_id)
);