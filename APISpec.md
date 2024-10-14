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

# Other Examples:

### 1.3. Visits - `/carts/visits/{visit_id}` (POST)

Shares the customers that visited the store on that tick. Not all
customers end up purchasing because they may not like what they see
in the current catalog.

**Request**:

```json
[
  {
    "customer_name": "string",
    "character_class": "string",
    "level": "number"
  },
  {
    ...
  }
]
```
**Response**:

```json
{
    "success": "boolean"
}
```

### 1.3. New Cart - `/carts/` (POST)

Creates a new cart for a specific customer.

**Request**:

```json
{
  "customer_name": "string",
  "character_class": "string",
  "level": "number"
}
```

**Response**:

```json
{
    "cart_id": "string" /* This id will be used for future calls to add items and checkout */
}
``` 

### 1.4. Add Item to Cart - `/carts/{cart_id}/items/{item_sku}` (PUT)

Updates the quantity of a specific item in a cart. 

**Request**:

```json
{
  "quantity": "integer"
}
```

**Response**:

```json
{
    "success": "boolean"
}
```

### 1.5. Checkout Cart - `/carts/{cart_id}/checkout` (POST)

Handles the checkout process for a specific cart.

**Request**:

```json
{
  "payment": "string",
}
```

**Response**:

```json
{
    "total_potions_bought": "integer",
    "total_gold_paid": "integer"
}
```

### 1.6. Search orders - `/carts/search/` (GET)
Searches for orders based on specified query parameters.

**Query Parameters**:

- `customer_name` (optional): The name of the customer.
- `potion_sku` (optional): The SKU of the potion.
- `search_page` (optional): The page number of the search results.
- `sort_col` (optional): The column to sort the results by. Possible values: `customer_name`, `item_sku`, `line_item_total`, `timestamp`. Default: `timestamp`.
- `sort_order` (optional): The sort order of the results. Possible values: `asc` (ascending), `desc` (descending). Default: `desc`.

**Response**:

The API returns a JSON object with the following structure:

- `previous`: A string that represents the link to the previous page of results. If there is no previous page, this value is an empty string.
- `next`: A string that represents the link to the next page of results. If there is no next page, this value is an empty string.
- `results`: An array of objects, each representing a line item. Each line item object has the following properties:
    - `line_item_id`: An integer that represents the unique identifier of the line item.
    - `item_sku`: A string that represents the SKU of the item. This includes the quantity and the name of the item.
    - `customer_name`: A string that represents the name of the customer who purchased the item.
    - `line_item_total`: An integer that represents the total cost of the line item.
    - `timestamp`: A string that represents the date and time when the line item was created. This is in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).


## 2. User Actions

The API calls are made in this sequence when the bottler comes:
1. `Post User`
2. `Post Preferences`
3. `Get Prefrence_Catalog`
4. `Post Shopping List`
5. `Add item (PUT)`
6. `Delete item`
7. `Get List History (Listory)`

### 2.1. Get Users
- `/bottler/plan` (POST)
### 2.1. Get Bottle Plan - `/bottler/plan` (POST)
### 2.1. Get Bottle Plan - `/bottler/plan` (POST)
### 2.1. Get Bottle Plan - `/bottler/plan` (POST)
### 2.1. Get Bottle Plan - `/bottler/plan` (POST)
### 2.1. Get Bottle Plan - `/bottler/plan` (POST)
### 2.1. Get Bottle Plan - `/bottler/plan` (POST)


### 2.1. Get Bottle Plan - `/bottler/plan` (POST)

Gets the plan for bottling potions.

**Response**:

```json
[
    {
        "potion_type": [r, g, b, d],
        "quantity": "integer"
    }
]
```

### 2.2. Deliver Bottles - `/bottler/deliver/{order_id}` (POST)

Posts delivery of potions. order_id is a unique value representing
a single delivery. 

**Request**:

```json
[
  {
    "potion_type": [r, g, b, d],
    "quantity": "integer"
  }
]
```

## 3. Barrel Purchases

The API calls are made in this sequence when Barrel Purchases can be made:
1. `Get Barrel Purchase Plan`
2. `Deliver Barrels`

### 3.1. Get Barrel Purchase Plan - `/barrels/plan` (POST)

Gets the plan for purchasing wholesale barrels. The call passes in a catalog of available barrels
and the shop returns back which barrels they'd like to purchase and how many.

**Request**:

```json
[
  {
    "sku": "string",
    "ml_per_barrel": "integer",
    "potion_type": "integer",
    "price": "integer",
    "quantity": "integer"
  }
]
```

**Response**:

```json
[
    {
        "sku": "string", /* Must match a sku from the catalog just passed in this call */
        "quantity": "integer" /* A number between 1 and the quantity available for sale */
    }
]
```

### 3.2. Deliver Barrels - `/barrels/deliver/{order_id}` (POST)

Posts delivery of barrels. order_id is a unique value representing
a single delivery.

**Request**:

```json
[
  {
    "sku": "string",
    "ml_per_barrel": "integer",
    "potion_type": "integer",
    "price": "integer",
    "quantity": "integer"
  }
]
```

### 4. Admin Functions

### 4.1. Reset Shop - `/admin/reset` (POST)

A call to reset shop will delete all inventory and in-flight carts and reset gold back to 100. The
shop should take this as an opportunity to remove all of their inventory and set their gold back to
100 as well.

### 5. Info Functions

### .1. Current time - `/info/current_time` (POST)

Shares what the latest time (in game time) is. 

**Request**:

```json
[
  {
    "day": "string",
    "hour": "number"
  }
]
```

### 6. Audit Functions

### 6.1. Get Inventory Summary - `/inventory/audit` (GET)

Return a summary of your current number of potions, ml, and gold.

**Response**:
```json
{
  "number_of_potions": "number",
  "ml_in_barrels": "number",
  "gold": "number"
)
```  

### 6.2 Get capacity purchase plan - `/inventory/plan` (POST)

What additional potion or ML capacity the shop would like to buy. Called once a day.
You start with 1 capacity of potion and 1 capacity of ml storage. Each potion capacity
allows 50 potion storage. Each ml capacity allows 10k of ml storage.

**Response**:
```json
{
  "potion_capacity": "number",
  "ml_capacity": "number"
}
```

### 6.3 Deliver capacity purchased - `/inventory/deliver` (POST)

Delivers capacity purchased back to shop. Called when a capacity purchase succeeds.

**Request**:
```json
{
  "potion_capacity": "number",
  "ml_capacity": "number"
}
```
