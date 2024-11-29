import os
from datetime import datetime
import sqlalchemy
from dotenv import load_dotenv
from faker import Faker
import numpy as np

# Load environment
load_dotenv()
engine = sqlalchemy.create_engine(os.environ.get("POSTGRES_URI"), use_insertmanyvalues=True)
fake = Faker()

# Simple configuration
NUM_USERS = 100000
NUM_STORES = 100
NUM_FOOD_ITEMS = 5000
ITEMS_PER_STORE = 1000
BATCH_SIZE = 1000

# Location settings
SLO_LAT = 35.3050
SLO_LONG = -120.6625

# Pre-defined data
STORE_NAMES = [
    "Trader Joe's", "Campus Market", "Village Market",
    "California Fresh Market", "Whole Foods Market",
    "Smart & Final", "Food 4 Less", "Grocery Outlet"
]

COMMON_ITEMS = [
    ("Milk", 64, 150, 8, 0, 0, 12, 12, 8),
    ("Bread", 20, 250, 1, 0, 2, 45, 3, 8),
    ("Eggs", 12, 70, 2, 0, 0, 0, 0, 6),
    ("Banana", 1, 105, 0, 0, 3, 27, 14, 1),
    ("Chicken Breast", 1, 120, 1, 0, 0, 0, 0, 26)
]

FOOD_CATEGORIES = {
    'Produce': ['Fresh', 'Organic', 'Local', 'Seasonal', 'Ripe'],
    'Dairy': ['Whole', 'Low-fat', 'Organic', 'Farm Fresh', 'Cultured'],
    'Meat': ['Fresh', 'Lean', 'Ground', 'Premium', 'Choice'],
    'Bakery': ['Fresh Baked', 'Artisan', 'Whole Grain', 'Gluten-Free', 'Homestyle'],
    'Pantry': ['Premium', 'Organic', 'Natural', 'Classic', 'Gourmet'],
    'Snacks': ['Crunchy', 'Sweet', 'Salty', 'Savory', 'Spicy'],
    'Beverages': ['Natural', 'Sparkling', 'Fresh', 'Premium', 'Classic']
}

FOOD_WORDS = [
    'Apple', 'Orange', 'Carrot', 'Potato', 'Spinach', 'Tomato', 'Cucumber',
    'Cheese', 'Yogurt', 'Cream', 'Butter', 'Cottage Cheese',
    'Beef', 'Pork', 'Turkey', 'Lamb', 'Fish',
    'Roll', 'Muffin', 'Cake', 'Cookie', 'Pastry',
    'Rice', 'Pasta', 'Beans', 'Soup', 'Cereal',
    'Chips', 'Crackers', 'Nuts', 'Popcorn', 'Pretzels',
    'Tea', 'Coffee', 'Juice', 'Soda', 'Water'
]

def reset_tables(conn):
    print("Resetting database tables...")
    conn.execute(sqlalchemy.text("""
        DROP TABLE IF EXISTS shopping_list_item CASCADE;
        DROP TABLE IF EXISTS shopping_list CASCADE;
        DROP TABLE IF EXISTS catalog_item CASCADE;
        DROP TABLE IF EXISTS catalog CASCADE;
        DROP TABLE IF EXISTS store CASCADE;
        DROP TABLE IF EXISTS food_item CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
        
        ALTER SEQUENCE IF EXISTS catalog_catalog_id_seq RESTART WITH 1;
        ALTER SEQUENCE IF EXISTS store_store_id_seq RESTART WITH 1;
        ALTER SEQUENCE IF EXISTS food_item_food_id_seq RESTART WITH 1;
        ALTER SEQUENCE IF EXISTS catalog_item_catalog_item_id_seq RESTART WITH 1;
        ALTER SEQUENCE IF EXISTS shopping_list_list_id_seq RESTART WITH 1;
    """))
    
    with open('init.sql', 'r') as file:
        sql = file.read()
        conn.execute(sqlalchemy.text(sql))
    print("Tables reset successfully")

def create_store_hours():
    now = datetime.now()
    open_time = now.replace(hour=8, minute=0)
    close_time = now.replace(hour=22, minute=0)
    return open_time, close_time

def generate_location(center_lat, center_long, spread):
    lat = center_lat + np.random.normal(0, spread)
    long = center_long + np.random.normal(0, spread)
    return lat, long

def generate_users(batch_size=1000):
    user_batches = []
    for i in range(0, NUM_USERS, batch_size):
        users = []
        for _ in range(min(batch_size, NUM_USERS - i)):
            lat, long = generate_location(SLO_LAT, SLO_LONG, 0.1)
            user = {
                "name": fake.unique.name(),
                "location": "San Luis Obispo",
                "longitude": long,
                "latitude": lat
            }
            users.append(user)
        user_batches.append(users)
    return user_batches

def generate_stores():
    stores = []
    # Add real stores
    for name in STORE_NAMES:
        lat, long = generate_location(SLO_LAT, SLO_LONG, 0.1)
        open_time, close_time = create_store_hours()
        store = {
            "name": name,
            "latitude": lat,
            "longitude": long,
            "open_time": open_time,
            "close_time": close_time,
            "catalog_id": None
        }
        stores.append(store)
    
    # Add generated stores
    remaining_stores = NUM_STORES - len(STORE_NAMES)
    for _ in range(remaining_stores):
        lat, long = generate_location(SLO_LAT, SLO_LONG, 0.1)
        open_time, close_time = create_store_hours()
        store = {
            "name": f"{fake.company()} Market",
            "latitude": lat,
            "longitude": long,
            "open_time": open_time,
            "close_time": close_time,
            "catalog_id": None
        }
        stores.append(store)
    return stores

def generate_food_items():
    food_items = []
    
    # Add common items first
    for name, size, cal, sat, trans, fiber, carb, sugar, protein in COMMON_ITEMS:
        food_items.append({
            "name": name,
            "serving_size": size,
            "calories": cal,
            "saturated_fat": sat,
            "trans_fat": trans,
            "dietary_fiber": fiber,
            "total_carbohydrate": carb,
            "total_sugars": sugar,
            "protein": protein
        })
    
    # Generate items for each category
    remaining_items = NUM_FOOD_ITEMS - len(COMMON_ITEMS)
    items_per_category = remaining_items // len(FOOD_CATEGORIES)
    
    for category, prefixes in FOOD_CATEGORIES.items():
        for _ in range(items_per_category):
            name = f"{np.random.choice(prefixes)} {np.random.choice(FOOD_WORDS)} {category}"
            food_items.append({
                "name": name,
                "serving_size": np.random.randint(1, 16),
                "calories": np.random.randint(0, 500),
                "saturated_fat": np.random.randint(0, 20),
                "trans_fat": np.random.randint(0, 2),
                "dietary_fiber": np.random.randint(0, 7),
                "total_carbohydrate": np.random.randint(0, 50),
                "total_sugars": np.random.randint(0, 25),
                "protein": np.random.randint(0, 25)
            })
    
    return food_items

def generate_shopping_lists_and_items(conn, user_ids, food_ids):
    print("Generating shopping lists and items...")
    
    lists_per_user = np.random.poisson(lam=2, size=len(user_ids))
    list_count = 0
    item_count = 0
    
    for i, user_id in enumerate(user_ids):
        num_lists = int(lists_per_user[i])
        
        for _ in range(num_lists):
            # Create shopping list
            result = conn.execute(
                sqlalchemy.text("""
                INSERT INTO shopping_list (name, user_id)
                VALUES (:name, :user_id)
                RETURNING list_id
                """),
                {
                    "name": np.random.choice(["Weekly", "Monthly", "Groceries", "Essentials"]),
                    "user_id": int(user_id)
                }
            )
            list_id = result.scalar_one()
            list_count += 1
            
            # Generate items for this list
            num_items = np.random.poisson(3)
            selected_foods = np.random.choice(food_ids, max(1, num_items), replace=False)
            
            list_items = []
            for food_id in selected_foods:
                list_items.append({
                    "list_id": int(list_id),
                    "food_id": int(food_id),
                    "user_id": int(user_id),
                    "quantity": int(np.random.randint(1, 5))
                })
                item_count += 1
            
            # Insert items in batches
            if list_items:
                conn.execute(
                    sqlalchemy.text("""
                    INSERT INTO shopping_list_item (list_id, food_id, user_id, quantity)
                    VALUES (:list_id, :food_id, :user_id, :quantity)
                    """),
                    list_items
                )
        
        if i % 1000 == 0:
            print(f"Processed shopping lists for user {i}/{len(user_ids)}")
            print(f"Current totals - Lists: {list_count}, Items: {item_count}")

print("Starting data generation...")

with engine.begin() as conn:
    reset_tables(conn)

    print("Generating users...")
    user_batches = generate_users()
    user_ids = []
    for batch in user_batches:
        for user in batch:
            result = conn.execute(
                sqlalchemy.text("""
                INSERT INTO users (name, location, longitude, latitude)
                VALUES (:name, :location, :longitude, :latitude)
                RETURNING user_id
                """),
                user
            )
            user_ids.append(result.scalar_one())
        print(f"Inserted user batch {len(user_ids)//1000}/{NUM_USERS//1000}")
        
    print("Generating stores...")
    stores = generate_stores()
    store_ids = []
    for store in stores:
        result = conn.execute(
            sqlalchemy.text("""
            INSERT INTO store (name, latitude, longitude, open_time, close_time)
            VALUES (:name, :latitude, :longitude, :open_time, :close_time)
            RETURNING store_id
            """),
            store
        )
        store_ids.append(result.scalar_one())
        
    print("Generating food items...")
    food_items = generate_food_items()
    food_ids = []
    for item in food_items:
        result = conn.execute(
            sqlalchemy.text("""
            INSERT INTO food_item (name, serving_size, calories, saturated_fat, 
                                trans_fat, dietary_fiber, total_carbohydrate, 
                                total_sugars, protein)
            VALUES (:name, :serving_size, :calories, :saturated_fat,
                    :trans_fat, :dietary_fiber, :total_carbohydrate,
                    :total_sugars, :protein)
            RETURNING food_id
            """),
            item
        )
        food_ids.append(result.scalar_one())

    print("Generating catalogs and catalog items...")
    for i, store_id in enumerate(store_ids, 1):
        catalog_id = conn.execute(
            sqlalchemy.text("""
            INSERT INTO catalog (store_id)
            VALUES (:store_id)
            RETURNING catalog_id
            """),
            {"store_id": store_id}
        ).scalar_one()
        
        # Common items first
        base_foods = food_ids[:5]
        other_foods = np.random.choice(food_ids[5:], ITEMS_PER_STORE - 5, replace=False)
        selected_foods = np.concatenate([base_foods, other_foods])
        
        catalog_items = []
        for food_id in selected_foods:
            base_price = np.random.lognormal(mean=1.5, sigma=0.5)
            catalog_items.append({
                "catalog_id": int(catalog_id),
                "food_id": int(food_id),
                "price": int(base_price * 100),
                "quantity": int(np.random.randint(10, 200))
            })

        for chunk in [catalog_items[i:i + 100] for i in range(0, len(catalog_items), 100)]:
            conn.execute(
                sqlalchemy.text("""
                INSERT INTO catalog_item (catalog_id, food_id, price, quantity)
                VALUES (:catalog_id, :food_id, :price, :quantity)
                """),
                chunk
            )
        print(f"Processed store {i}/{len(store_ids)}")
    
    print("Generating shopping lists and items...")
    generate_shopping_lists_and_items(conn, user_ids, food_ids)

print("Data generation complete")