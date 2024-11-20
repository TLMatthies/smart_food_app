# Example workflow

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
