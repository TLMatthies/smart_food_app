# Scenario 1

Bob wants to create an account and buy chicken from Trader Joe's. He will:

1. Create a user account for himself
2. View the list of stores to find Trader Joe's
3. View Trader Joe's catalog to check the chicken price

# Testing results

## 1. Create Bob's user account

```bash
curl -X 'POST' \
  'https://smart-food-app.onrender.com/users/' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Bob",
  "location": "San Luis Obispo"
}'
```

Response:

```json
{
  "user_id": 5
}
```

## 2. Get list of stores to find Trader Joe's

```bash
curl -X 'GET' \
'http://127.0.0.1:8000/stores/' \
-H 'accept: application/json' \
-H 'access_token: fartsmella21'
```

Response:

```json
[
  {
    "store_id": "2",
    "name": "Campus Market",
    "hours": ["2024-10-25 08:00:00", "2024-10-30 21:00:00"],
    "location": {
      "latitude": 150,
      "longitude": 150
    }
  },
  {
    "store_id": "1",
    "name": "Trader Joes",
    "hours": ["2024-10-28 08:30:00", "2024-10-30 09:00:00"],
    "location": {
      "latitude": 150,
      "longitude": 150
    }
  }
]
```

## 3. View Trader Joe's catalog

```bash
curl -X 'GET' \
  'https://smart-food-app.onrender.com/stores/1/catalog' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21'
```

Response:

```json
[
  {
    "item_sku": "1",
    "name": "Grilled Chicken",
    "quantity": 12,
    "price": 1099
  }
]
```

# Scenario 2

Carl creates a shopping list under $10:

1. Create user account for Carl
2. Set Carl's budget preference
3. Get Trader Joe's catalog
4. Create new shopping list
5. Add items to list

# Testing results

## 1. Create Carl's user account

```bash
curl -X 'POST' \
  'https://smart-food-app.onrender.com/users/' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Carl",
  "location": "San Luis Obispo"
}'
```

Response:

```json
{
  "user_id": 9
}
```

## 2. Set Carl's budget preference

```bash
curl -X 'POST' \
  'https://smart-food-app.onrender.com/users/users/6/preferences?budget=1000' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21' \
  -d ''
```

Response:

```json
"OK"
```

## 3. Get Trader Joe's catalog

```bash
curl -X 'GET' \
  'https://smart-food-app.onrender.com/stores/1/catalog' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21'
```

Response:

```json
[
  {
    "item_sku": "1",
    "name": "Grilled Chicken",
    "quantity": 12,
    "price": 1099
  }
]
```

## 4. Create new shopping list

```bash
curl -X 'POST' \
  'https://smart-food-app.onrender.com/users/users/6/lists?name=Groceries' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21' \
  -d ''
```

Response:

```json
{
  "name": "Groceries",
  "list_id": 4
}
```

## 5. Add items to list

```bash
curl -X 'GET' \
curl -X 'POST' \
  'https://smart-food-app.onrender.com/users/users/{user_id}/lists/4' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "food_id": 1,
    "quantity": 1
  }
]'
```

Response:

```json
"OK"
```

# Example workflow 3

Carl changes his budget preferences and deletes a shopping list:

1. Update Carl's budget preference
2. Get Carl's shopping lists
3. Delete shopping list

# Testing results

## 1. Update Carl's budget preference

```bash
curl -X 'POST' \
  'https://smart-food-app.onrender.com/users/users/6/preferences?budget=1200' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21' \
  -d ''
```

Response:

```json
"OK"
```

## 2. Get Carl's shopping lists

```bash
curl -X 'GET' \
  'https://smart-food-app.onrender.com/users/users/6/lists/}' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21'
```

Response:

```json
[
  {
    "list_id": 4,
    "name": "Groceries"
  }
]
```

## 3. Create a list to delete

```bash
curl -X 'DELETE' \
  'https://smart-food-app.onrender.com/users/users/{user_id}/lists/4}?food_id=1' \
  -H 'accept: application/json' \
  -H 'access_token: fartsmella21'
```

Response:

```json
"OK"
```