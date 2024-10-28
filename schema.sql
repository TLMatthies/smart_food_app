-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT
);

-- Stores table
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL
);

-- Food items table
CREATE TABLE food_items (
    food_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    calories INTEGER,
    protein INTEGER,
    total_carbohydrate INTEGER,
    total_sugars INTEGER,
    total_fat INTEGER,
    saturated_fat INTEGER,
    dietary_fiber INTEGER,
    trans_fat INTEGER
);

-- Catalog items table (joins stores and food items)
CREATE TABLE catalog_items (
    catalog_item_id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores(store_id),
    food_id INTEGER REFERENCES food_items(food_id),
    price INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    UNIQUE(store_id, food_id)
);