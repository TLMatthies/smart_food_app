-- Users table
create table
  public."Users" (
    user_id integer generated by default as identity not null,
    name text null,
    location text null,
    constraint User_pkey primary key (user_id)
  ) tablespace pg_default;

-- Stores table
create table
  public.store (
    store_id integer generated by default as identity not null,
    name text null,
    catalog_id integer null,
    latitude double precision null,
    longitude double precision null,
    open_time timestamp without time zone null,
    close_time timestamp without time zone null,
    constraint store_pkey primary key (store_id)
  ) tablespace pg_default;

INSERT INTO store(name, catalog_id, latitude, longitude, open_time, close_time)
VALUES ('Trader Joes', 1, 120, 150, 2024-10-28 08:30:00, 2024-10-30 09:00:00),
('Campus Market', 2, 150, 130, 2024-10-25 08:00:00, 2024-10-30 21:00:00);

-- Food items table
create table
  public.food_item (
    food_id integer generated by default as identity not null,
    name text null,
    serving_size text null,
    calories integer null,
    saturated_fat integer null,
    trans_fat integer null,
    dietary_fiber integer null,
    total_carbohydrate integer null,
    total_sugars integer null,
    protein integer null,
    constraint food_item_pkey primary key (food_id)
  ) tablespace pg_default;
  INSERT INTO food_item(name, serving_size, calories, saturated_fat, trans_fat, dietary_fiber, total_carbohydrate, total_sugars, protein)
  VALUES ('Grilled Chicken', 4, 200, 15, 5, 0, 0, 0, 30),
  ('Oreos', 8, 1000, 200, 250, 0, 0, 190, 0);

-- Catalog table (allows stores to have multiple catalogs)
create table
  public.catalog (
    catalog_id integer generated by default as identity not null,
    store_id integer null,
    constraint catalog_pkey primary key (catalog_id)
  ) tablespace pg_default;
INSERT INTO catalog(catalog_id, store_id)
VALUES (1, 1),
(2, 2);

-- Catalog Items table (joins specific catalogs with food items and their associated prices)
create table
  public.catalog_item (
    catalog_item_id integer generated by default as identity not null,
    catalog_id integer null,
    food_id integer null,
    price integer null,
    quantity integer null,
    constraint catalog_item_pkey primary key (catalog_item_id),
    constraint catalog_item_catalog_id_fkey foreign key (catalog_id) references catalog (catalog_id),
    constraint catalog_item_food_id_fkey foreign key (food_id) references food_item (food_id)
  ) tablespace pg_default;
  INSERT INTO catalog_item(catalog_id, food_id, price, quantity)
  VALUES(1, 1, 1099, 12),
  (2, 1, 1000099, 2),
  (2, 2, 1799, 15);

  create table
  public.preference (
    user_id integer not null,
    budget integer null,
    constraint preference_pkey primary key (user_id),
    constraint preference_user_id_fkey foreign key (user_id) references "Users" (user_id)
  ) tablespace pg_default;

  create table
  public.shopping_list (
    list_id integer generated by default as identity not null,
    name text null,
    user_id integer null,
    constraint shopping_list_pkey primary key (list_id),
    constraint shopping_list_user_id_fkey foreign key (user_id) references "Users" (user_id)
  ) tablespace pg_default;

  create table
  public.shopping_list_item (
    list_id integer not null,
    food_id integer not null,
    quantity integer null,
    constraint shopping_list_item_pkey primary key (list_id, food_id),
    constraint shopping_list_item_food_id_fkey foreign key (food_id) references food_item (food_id),
    constraint shopping_list_item_list_id_fkey foreign key (list_id) references shopping_list (list_id)
  ) tablespace pg_default;
