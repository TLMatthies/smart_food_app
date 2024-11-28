# API Specification for The Crusty Kart

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
        "store_id": "string", /* Matching regex ^[a-zA-Z0-9_]{1,20}$ */
        "name": "string",
        "hours": ["open_time", "close_time"], /* 24 hour timestamp format */
        "location": {
            "latitude": "float", /* Between -90 and 90 */
            "longitude": "float" /* Between -180 and 180 */
        }
    }
]
```

### 1.2. Get Catalog - `/stores/{store_id}/catalog` (GET)

Retrieves the list of items that the store has in its catalog.

**Response**:

```json
[
    {
        "item_sku": "string", /* Matching regex ^[a-zA-Z0-9_]{1,20}$ */
        "name": "string",
        "quantity": "integer",
        "price": "integer" /* In cents, between 1 and 1000000 */
    }
]
```

### 1.3. Compare Prices - `/stores/compare-prices` (POST) /* New complex endpoint */

Compare prices across stores for a specific item.

**Request**:

```json
{
    "food_id": "integer",
    "max_price": "integer", /* Optional, in cents */
    "max_stores": "integer" /* Optional, defaults to 3 */
}
```

**Response**:

```json
[
    {
        "store_id": "integer",
        "store_name": "string",
        "price": "integer", /* In cents */
        "rank": "integer"
    }
]
```

## 2. User Info

The API calls are made in this sequence:
1. `Post User`
2. `Post Preferences`
3. `Get Preferences`
4. `Post Shopping List`
5. `Add Items to List`
6. `Delete Item`
7. `Get List History`

### 2.1. Create new user - `/users/` (POST)

Creates a new user with name and optional location.

**Request**:

```json
{
    "name": "string",
    "location": "string", /* Optional, default: "Calpoly SLO" */
    "latitude": "float", /* Optional, default: 35.3050 */
    "longitude": "float" /* Optional, default: 120.6625 */
}
```

**Response**:

```json
{
    "user_id": "integer"
}
```

### 2.2. Add user preferences - `/users/{user_id}/preferences` (POST)

Adds user budget preference.

**Request**:

```json
{
    "budget": "integer" /* In cents, must be greater than 0 */
}
```

### 2.3. Get user's preferences - `/users/{user_id}/preferences` (GET)

Get the user's preferences.

**Response**:

```json
{
    "budget": "integer" /* In cents */
}
```

### 2.4 Make a shopping list - `/users/{user_id}/lists` (POST)

Creates a new shopping list for a user.

**Request**:

```json
{
    "name": "string"
}
```

**Response**:

```json
{
    "list_id": "integer",
    "name": "string"
}
```

### 2.5 Add items to a list - `/users/{user_id}/lists/{list_id}` (POST)

Add items to specified list for a user.

**Request**:

```json
[
    {
        "food_id": "integer",
        "quantity": "integer" /* Must be greater than 0 */
    }
]
```

**Response**:

```json
{
    "message": "Foods successfully added to list"
}
```

### 2.6 Delete item from list - `/users/{user_id}/lists/{list_id}` (DELETE)

Remove a specific item from a list.

**Response**: Status 204 No Content

### 2.7 Get list history - `/users/{user_id}/lists` (GET)

Get all shopping lists for a user.

**Response**:

```json
[
    {
        "list_id": "integer",
        "name": "string"
    }
]
```

## 3. Shopping Route

### 3.1. Route Optimization - `/shopping/route-optimize` (POST) /* New complex endpoint */

Find optimal store based on location and preferences.

**Request**:

```json
{
    "user_id": "integer",
    "food_id": "integer",
    "use_preferences": "boolean"
}
```

**Response** (when use_preferences=false):

```json
{
    "Closest Store": {
        "Name": "string",
        "Store ID": "string",
        "Distance Away": "string", /* In kilometers */
        "Price of Item": "integer" /* In cents */
    }
}
```

**Response** (when use_preferences=true):

```json
{
    "Closest Store": {
        "Name": "string",
        "Store ID": "string",
        "Distance Away": "string", /* In kilometers */
        "Price of Item": "integer" /* In cents */
    },
    "Best Value Store": {
        "Name": "string",
        "Store ID": "string",
        "Distance Away": "string", /* In kilometers */
        "Price of Item": "integer" /* In cents */
    }
}
```
