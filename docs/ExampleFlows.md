# Scenario 1: Joe creates an account and views Trader Joe's catalogue

First, Joe must create a user account, then checks a list of the stores, then gets the catalogue of Trader Joes. To do this he:
1. Joe starts by calling `POST /users` to create an account.
2. Then Joe calls `GET /stores` to get a list of the stores available in the app, along with the store IDs.
3. Finally, Joe calls `GET /stores/{store_id}/catalogue`, using the ID of Trader Joe's.

Joe now has a list of the catalogue items at Trader Joe's.

---

# Scenario 2: Bob creates a shopping list under $10

First Bob must establish his preferences, then he can look through the catalogue of all stores, with his set parameters, and then add them to a cart.
1. Bob starts by calling `PUT users/{user_id}/preferences` to set the maximum price per item to $10.
2. Then Bob calls `GET stores/catalogue?budget<10` to find all items where the value is under $10.
3. Next, Bob calls `POST users/{user_id}/shopping_list` to create a shopping cart.
4. Finally, Bob calls `PUT users/{user_id}/{list_id}/item` with the request body `{sku: cheese, quantity: 1}`, using the list ID generated from making the cart.

Bob now has a shopping list with an item added to it that is priced under $10.

---

# Scenario 3: Carl changes his budget preferences and deletes a shopping list

First, Carl must edit his preferences, then go and delete the list.
1. Carl starts by calling `PUT users/{user_id}/preferences` to set the maximum price per item to $8, replacing his last set of preferences.
2. Then Carl calls `GET users/{user_id}/shopping_lists` to get the shopping list IDs of all the shopping lists he has.
3. Finally, Carl calls `DELETE users/{user_id}/{list_id}` to remove the desired shopping list.
