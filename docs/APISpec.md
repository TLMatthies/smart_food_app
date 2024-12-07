# API Specification for The Crusty Kart

This API enables users to find stores, compare prices, manage shopping lists, and optimize shopping routes based on location and budget.

## 1. Store Info

The API calls are made in this sequence when making a purchase:

1. `Get Stores`
2. `Get Catalog`
3. `Compare Prices`

### 1.1. Get Stores - `/stores/` (GET)

Retrieves the list of stores. Each store has a store ID, Name, hours, location.

**Response**:

```json
[
    {
        "store_id": "integer",
        "name": "string",
        "hours": {
            "open": "string",  /* 12-hour format with AM/PM (e.g., "08:00 AM") */
            "close": "string"  /* 12-hour format with AM/PM (e.g., "10:00 PM") */
        },
        "location": {
            "latitude": "float",  /* Between -90 and 90 */
            "longitude": "float"  /* Between -180 and 180 */
        }
    }
    ...
]
```

### 1.2. Get Catalog - `/stores/{store_id}/catalog` (GET)

Retrieves the list of items that the store has in its catalog.

**Parameters**:

- `store_id` (path parameter): ID of the store to get catalog from

**Response**:

```json
[
    {
        "food_id": "integer",
        "item": "string",
        "quantity": "integer",
        "price": "string"  /* Format: "$X.XX" */
    }
    ...
]
```

### 1.3. Compare Prices - `/stores/compare-prices` (POST)

Compare prices across stores for a specific item.

**Request**:

```json
{
  "food_id": "integer",
  "max_stores": "integer" /* Optional, default: 3 */
}
```

**Response**:

```json
[
    {
        "store_id": "integer",
        "store_name": "string",
        "item": "string",
        "price": "string",  /* Format: "$X.XX" */
        "rank": "integer"   /* Ranking by price, starting from 1 */
    }
    ...
]
```

### Error Responses

All endpoints may return the following errors:

- 401 Unauthorized: Invalid or missing access token
- 404 Not Found: Resource not found (store, food item)
- 500 Internal Server Error: Server-side error

Specific errors:

- GET `/stores/{store_id}/catalog`:
  - 404: "Store not found :("
- POST `/stores/compare-prices`:
  - 404: "Food_id does not exist"
  - 400: "Invalid max_stores parameter"

## 2. User Info

### 2.1. Create new user - `/users/` (POST)

Creates a new user with name and optional location information.

**Request**:

```json
{
  "name": "string" /* Required: Matches regex ^[a-zA-Z0-9_]+$, length 1-27 */,
  "location": "string" /* Optional: Default "Calpoly SLO" */,
  "latitude": "float" /* Optional: Default 35.3050, between -90 and 90 */,
  "longitude": "float" /* Optional: Default -120.6625, between -180 and 180 */
}
```

**Response**:

```json
{
  "user_id": "integer"
}
```

### 2.2. Get list history - `/users/{user_id}/lists/` (GET)

Get all shopping lists for a user.

**Parameters**:

- `user_id` (path parameter): ID of the user

**Response**:

```json
[
  {
    "list_id": "integer",
    "name": "string"
  }
]
```

### 2.3. Get list nutritional facts - `/users/{user_id}/lists/{list_id}/facts` (GET)

Get nutritional information for all items in a shopping list.

**Parameters**:

- `user_id` (path parameter): ID of the user
- `list_id` (path parameter): ID of the shopping list

**Response**:

```json
{
    "Item Name 1": {
        "total_servings": "integer",
        "total_saturated_fat": "integer",
        "total_trans_fat": "integer",
        "total_dietary_fiber": "integer",
        "total_carbohydrates": "integer",
        "total_sugars": "integer",
        "total_protein": "integer",
        "total_calories": "integer"
    },
    "Item Name 2": {
        "total_servings": "integer",
        "total_saturated_fat": "integer",
        "total_trans_fat": "integer",
        "total_dietary_fiber": "integer",
        "total_carbohydrates": "integer",
        "total_sugars": "integer",
        "total_protein": "integer",
        "total_calories": "integer"
    },
    ...
    /* Total: Sum of previous totals */
    "Total": {
        "total_servings": "integer",
        "total_saturated_fat": "integer",
        "total_trans_fat": "integer",
        "total_dietary_fiber": "integer",
        "total_carbohydrates": "integer",
        "total_sugars": "integer",
        "total_protein": "integer",
        "total_calories": "integer"
    }
}
```

- 204 No Content: "List is empty, add something to it!"

### 2.4. Create shopping list - `/users/{user_id}/lists` (POST)

Create a new shopping list for a user.

**Parameters**:

- `user_id` (path parameter): ID of the user
- `name` (query parameter): Name of the shopping list

**Response**:

```json
{
  "name": "string",
  "list_id": "integer"
}
```

### 2.5. Add items to list - `/users/{user_id}/lists/{list_id}/item` (POST)

Add one or more items to a shopping list.

**Parameters**:

- `user_id` (path parameter): ID of the user
- `list_id` (path parameter): ID of the shopping list

**Request**:

```json
[
  {
    "food_id": "integer",
    "quantity": "integer" /* Must be greater than 0 */
  }
]
```

**Response**: "Foods successfully added to list"

### 2.6. Delete item from list - `/users/{user_id}/lists/{list_id}/item` (DELETE)

Remove a specific item from a shopping list.

**Parameters**:

- `user_id` (path parameter): ID of the user
- `list_id` (path parameter): ID of the shopping list
- `food_id` (query parameter): ID of the food item to remove

**Response**: Status 204 No Content

### 2.7. Delete entire list - `/users/{user_id}/list/{list_id}/` (DELETE)

Delete an entire shopping list and all its items.

**Parameters**:

- `user_id` (path parameter): ID of the user
- `list_id` (path parameter): ID of the shopping list

**Response**: Status 204 No Content

### 2.8. Get list contents - `/users/{user_id}/list/{list_id}` (GET)

Get all items in a specific shopping list.

**Parameters**:

- `user_id` (path parameter): ID of the user
- `list_id` (path parameter): ID of the shopping list

**Response**:

```json
[
  {
    "food_id": "integer",
    "name": "string",
    "quantity": "integer"
  },
  ...
]
```

### 2.9. Edit Item Quantity in List - `/users/{user_id}/lists/{list_id}/item` (PUT)

Edits the quantity of one or more existing items within a specified shopping list.

**Parameters**:

- `user_id` (path parameter): ID of the user
- `list_id` (path parameter): ID of the shopping list

**Request**:

```json
[
  {
    "food_id": "integer",
    "quantity": "integer" /* Must be greater than 0 */
  }
  ...
]
```

**Response**: Status 204 No Content

### Error Responses

All endpoints may return these errors:

- 401 Unauthorized: Invalid or missing access token
- 404 Not Found: Various cases including:
  - "User does not exist"
  - "List does not exist"
  - "User is not associated with this list"
  - "Food ID not recognized"
  - "Food ID(s) not found in the user's list"
- 409 Conflict: "Duplicate item in list" (for adding items)
- 500 Internal Server Error: Various server-side errors

## 3. Shopping Route

### 3.1. Route Optimization - `/shopping/route_optimize` (GET)

Finds nearby stores with a given food item, taking into account optional budget constraints.

**Parameters**:

- `user_id`: ID of the user
- `food_id`: ID of the food item to find
- `budget`: Optional budget in cents, default is 0 (no budget limit)

**Response**:

```json
{
  "Closest Store": {
    "Name": "string",
    "Store ID": "integer",
    "Distance Away": "string" /* Format: "X.XX km" */,
    "Price of Item": "string" /* Format: "$X.XX" */
  },
  "Best Value Store": {
    "Name": "string",
    "Store ID": "integer",
    "Distance Away": "string" /* Format: "X.XX km" */,
    "Price of Item": "string" /* Format: "$X.XX" */
  }
}
```

### 3.2. Fulfill Shopping List - `/shopping/{user_id}/fulfill_list/{list_id}` (GET)

Generate a list of closest stores to fulfill a shopping list.

**Parameters**:

- `user_id`: ID of the user
- `list_id`: ID of the shopping list
- `budget`: Optional maximum willing to spend per item in cents (default: maximum integer)
- `max_dist`: Optional maximum range in km (default: 10)
- `order_by`: Optional sorting option (1=price,distance; 2=price; 3=distance) (default: 1)

**Response**:

```json
[
  {
    "Name": "string",
    "Store ID": "integer",
    "Distance Away": "string" /* Format: "X.XX km" */,
    "Item": "string",
    "Price of Item": "string" /* Format: "$X.XX" */
  }
]
```

### 3.3. Find Snack - `/shopping/{user_id}/find_snack/{food_id}` (GET)

Find the closest store that has a specific food item.

**Parameters**:

- `user_id`: ID of the user
- `food_id`: ID of the food item
- `max_dist`: Optional maximum range in km (default: 10)
- `order_by`: Optional sorting option (1=price,distance; 2=price; 3=distance) (default: 3)

**Response**:

```json
{
  "Name": "string",
  "Store ID": "integer",
  "Distance Away": "string" /* Format: "X.XX km" */,
  "Item": "string",
  "Price of Item": "string" /* Format: "$X.XX" */
}
```

### Error Responses

All endpoints may return:

- 401 Unauthorized: Invalid or missing access token
- 404 Not Found:
  - "User does not exist"
  - "Food_id does not exist"
  - "No stores found with given parameters"
  - "No stores in range"
- 400 Bad Request: "Invalid order_by option"
