# API Specification for the Smart Food App

## 1. Store Info

The API calls are made in this sequence when making a purchase:
1. `Get Stores`
2. `Get Catalog`

### 1.1. Get Stores - `/stores/` (GET)


Retrieves the list of stores. Each store has a store ID, Name, hours, location

**Response**:

```json
[
    {
        "store_id": "string", /* Matching regex ^[a-zA-Z0-9_]{1,20}$ */
        "name": "string",
        "hours": "(open, close)", /* integer between 0 and 23 */
        "location": "coordinates", /* latitude longitude */
    }
]
```

### 1.2. Get Catalog - `/stores/{store_id}/catalog` (GET)

Retrieves the list of items that the store has in its catalog, item_sku, name, price, quantity

**Response**:

```json
[
    {
        "item_sku": "string", /* Matching regex ^[a-zA-Z0-9_]{1,20}$ */
        "store_id": "string", /* Foreign key to store_id */
        "name": "string",
        "quantity": "integer",
        "price": "integer", /* Between 1 and 10000 */
    },
]
```

## 2 User info
1. `Post User`
2. `Post Preferences`
3. `Get Prefrence_Catalog`
4. `Post Shopping List`
5. `Add item (PUT)`
6. `Delete item`
7. `Get List History (Listory)`

### 2.1. Create new user - `/users/` (POST)
Creates a new user, with id and name

**Request**:
```json

    {
        "name": "string"
    }

```

**Response**:
```json

    {
        "user_id": "int"
    }

```
### 2.2 Add user preferences - `/users/{user_id}/preferences` (POST)
Adds user preference onto user account (only budget for now)

**Request**:
```json
[
    {
        "budget": "int"
    }
]
```
### 2.3 Get user's preferences - `/users/{user_id}/prefernces` (GET)
Get the user's preferences

**Response**:
```json
[
    {
        "budget": "int"
    }
]
```

### 2.4 Make a shopping list - `/users/{user_id}/lists` (POST)
Make a new shopping list for customer

**Request**:
```json

{
    "name": "string"
}
```

**Response**:
```json

{
    "list_id": "int"
    "name": "string"
}

```

### 2.5 Add items to a list - `/users/{user_id}/lists/{list_id}` (PUT)
Add items to specified list, and specified user

**Request**:
```json
[
    {
        "sku": "string"
        "quantity": "int"
    },
    {
        ...
    }
]
```

### 2.6 Delete item from list - `/users/{user_id}/lists/{list_id}/{sku}` (DELETE)
Remove a certain item from a certain list


### 2.7 Get list history - `/users/{user_id}/lists` (GET)

**Response**:
```json
[
    {
        "list_id": "int"
        "name": "string"
    },
    {
        ...
    }
]
```

