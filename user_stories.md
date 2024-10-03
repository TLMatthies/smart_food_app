# User Stories and Exceptions

## User Stories

1. **As a budget-conscious college student**, I want to find the cheapest grocery options, **so that** I can eat well without overspending.

2. **As a health-conscious shopper**, I want to see the nutritional information of food items, **so that** I can maintain a balanced diet.

3. **As a time-strapped husband**, I want to optimize my shopping route, **so that** I can save time on grocery trips.

4. **As a new student at Cal Poly**, I want to discover nearby grocery stores, **so that** I can easily access food options.

5. **As a person without a car**, I want to find grocery stores within walking distance or along bus routes, **so that** I can shop conveniently.

6. **As an environmentally-conscious consumer**, I want to minimize my travel distance for shopping, **so that** I can reduce my carbon footprint.

7. **As a bargain hunter**, I want to receive notifications about sales and discounts, **so that** I can save money on groceries.

8. **As a meal planner**, I want to generate shopping lists based on recipes, **so that** I can prepare meals efficiently.

9. **As a supporter of local businesses**, I want to find locally-sourced products, **so that** I can support my community.

10. **As a student on a tight budget**, I want to find free food resources and events, **so that** I can supplement my meals.

11. **As a social person**, I want to share my shopping list with friends, **so that** we can coordinate and shop together.

12. **As a vegan**, I want to filter grocery items by dietary preference, **so that** I can find suitable food options.

## Exceptions

1. **Invalid Location Input**  
   _Exception:_ If a user inputs an invalid location, the system should prompt them to enter a valid address or allow manual selection on a map.

2. **Unavailable Store Data**  
   _Exception:_ If a store's data is unavailable or outdated, the system should notify the user and provide alternative stores.

3. **Scheduling Conflicts**  
   _Exception:_ If the user tries to schedule a shopping trip outside store operating hours, the system should alert them and suggest available times.

4. **Dietary Restrictions Conflict**  
   _Exception:_ If the user's dietary restrictions conflict with selected items, the system should warn them and suggest suitable alternatives.

5. **Budget Insufficiency**  
   _Exception:_ If the user's budget is insufficient for their shopping list, the system should notify them and offer cheaper options.

6. **Item Out of Stock**  
   _Exception:_ If an item in the shopping list is out of stock, the system should inform the user and recommend substitutes.

7. **Location Services Disabled**  
   _Exception:_ If the app cannot access location services due to permissions, it should request access or allow manual input.

8. **Internet Connection Lost**  
   _Exception:_ If the user loses internet connection during use, the system should save progress and notify the user.

9. **Missing Nutritional Information**  
   _Exception:_ If there is an error in retrieving nutritional information, the system should alert the user and proceed with available data.

10. **Invalid Nutritional Goals**  
    _Exception:_ If the user enters unrealistic nutritional goals (e.g., negative calories), the system should validate input and prompt for correction.

11. **No Contacts for Sharing**  
    _Exception:_ If the user tries to share a shopping list but no contacts are available, the system should prompt them to add contacts.

12. **Critical System Error**  
    _Exception:_ If the system encounters a critical error, it should display an error message and provide options to report the issue or restart.
