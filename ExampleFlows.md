Joe comes to the smart food app looking to get a list of the items from a Trader Joes

First, Joe must create a user account, then checks a list of the stores, then gets the catalogue of Trader Joes. To do this he:

starts by calling POST /users to create an account
then Joe calls GET /stores to get a list of the stores avaiable in the app, along with the store ids
finally, Joe calls GET /stores/{store_id}/catalogue, using the ID of Trader Joes
Joe now has a list of the catalogue items at Trader Joes


Bob, an established user of the smart food app wants to stay in budget by not buying items over 10$ while making a food plan.

First Bob must establish his preferences, then he can look through the catalogue of all stores, with his set parameters, and then add them to a cart

starts by calling PUT users/{user_id}/preferences to set the maximum price per item to 10$
then Bob calls GET stores/catalogue?budget<10 to find all items where the value is under 10$
then Bob calls POST users/{user_id}/shopping_list to make a shopping cart
finally Bob calls PUT users/{user_id}/{list_id}/item with request {sku: cheese quantity: 1}, using the list id generated from making the cart
Bob now has a shopping list with an item added to it that has been sorted to be less than 10$.


Carl, another established user of the app wants to change his budget preferences and then delete a shopping list he has created

First, Carl must edit his preferences, then go and delete the list.

starts by calling PUT users/{user_id}/preferences to set the maximum price per item to 8$, replacing his last set of preferences
then Carl calls GET users/{user_id}/shopping_lists to get the shopping list ids of all the shopping lists he has.
finally Carl calls DELETE users/{user_id}/{list_id} to remove the desired shopping list
