# Code Review and API Design Comments

## Aiden King

### Code Review Comments
1. **(No Plans For Implementation)**  
   - Shopping path depends on Auth. Creating keys for individual users is out of scope.

2. **(Addressed and Implemented)**  
   - Removed duplicate functionality.

3. **(Addressed and Implemented)**  
   - `Hours` class created.

4. **(Addressed and Implemented)**  
   - Code moved out of the `with` block.

5. **(Addressed and Implemented)**  
   - Hours now properly identify opening and closing times.

6. **(Addressed and Implemented)**  
   - Fixed broken query; now functions correctly.

7. **(Addressed and Implemented)**  
   - Updated `try` and `except` statements for consistency.

8. **(Addressed and Implemented)**  
   - Applied the above fix to `users.py`.

9. **(Addressed and Implemented)**  
   - `scalar_one()` now raises exceptions properly.

10. **(No Plans For Implementation)**  
    - Preferences removed; no longer applies.

11. **(Addressed and Implemented)**  
    - Double path declarations removed.

12. **(Addressed and Implemented)**  
    - `mappings().all()` used for improved clarity.

---

### Schema/API Design
1. **(Addressed and Implemented)**  
   - Table `Users` is now lowercase for consistency.

2. **(Addressed and Implemented)**  
   - Distance functionality implemented in the `Optimize Shopping Route` endpoint.

3. **(Addressed and Implemented)**  
   - `name` field is no longer nullable.

4. **(Addressed and Implemented)**  
   - Fixed starter population data.

5. **(Addressed and Implemented)**  
   - Foreign key introduced correctly.

6. **(Addressed and Implemented)**  
   - Preferences (budget) handled at runtime.

7. **(Addressed and Implemented)**  
   - Primary key of `shopping_lists` now auto-generates.

8. **(No Plans For Implementation)**  
   - Preferences table removed; no longer applicable.

9. **(Addressed and Implemented)**  
   - API routes fixed to remove duplicates.

10. **(Addressed and Implemented)**  
    - Fixed location return in the API spec.

11. **(Addressed and Implemented)**  
    - Fixed additional issues in the API spec.

12. **(Addressed and Implemented)**  
    - Resolved further inconsistencies in the API spec.

13. **(No Plans For Implementation)**  
    - Preferences removed, now handled at runtime.

---

### Suggested Endpoints
1. **(Addressed and Implemented)**  
   - Integrated into the `Optimize Shopping Route` endpoint.

2. **(No Plans For Implementation)**  
   - No upsert implementation to avoid unnecessary complexity. Similar functionality can be achieved using delete and add.

3. **(Addressed and Implemented)**  
   - List Visualizer endpoint implemented.

---

## Megan Fung

### Code Review Comments
1. **(No Plans For Implementation)**  
   - Duplicate functions were a mistake and removed.

2. **(Addressed and Implemented)**  
   - All functions now return proper HTTP codes.

3. **(Addressed and Implemented)**  
   - Extra `}` removed.

4. **(Addressed and Implemented)**  
   - Naming conventions standardized.

5. **(No Plans For Implementation)**  
   - Query visibility within the function is preferred for ease of updates.

6. **(Addressed and Implemented)**  
   - Refactored functions to use `mappings()` for cleaner code.

7. **(Addressed and Implemented)**  
   - Added default values for functions.

8. **(Addressed and Implemented)**  
   - Same fix as Aiden King’s Code Review #9.

9. **(No Plans For Implementation)**  
   - Refactored endpoints; nesting would lead to inefficiencies (e.g., `create_user` being alone).

10. **(Addressed and Implemented)**  
    - Data types clarified in functions.

11. **(Addressed and Implemented)**  
    - Error handling overhauled across all functions.

12. **(No Plans For Implementation)**  
    - Explained `POST` vs `PUT` usage in context (e.g., adding/updating items in a cart).

---

### Schema/API Design
1. **(Addressed and Implemented)**  
   - Redundant ID removed.

2. **(No Plans For Implementation)**  
   - Coupled food items with nutritional info; no separate table.

3. **(Will Be Implemented)**  
   - Scheduled for V5.

4. **(No Plans For Implementation)**  
   - Avoided cluttering tables for better scaling performance.

5. **(No Plans For Implementation)**  
   - Store names need not be unique (e.g., multiple Trader Joe’s).

6. **(Addressed and Implemented)**  
   - Added checks to prevent invalid data (e.g., negative budget).

7. **(No Plans For Implementation)**  
   - Monetary data stored in cents (e.g., 10.99 → 1099).

8. **(Addressed and Implemented)**  
   - Standardized IDs as `bigint`.

9. **(No Plans For Implementation)**  
   - Avoided cascading deletes for scalability and multi-user scenarios.

10. **(No Plans For Implementation)**  
    - Avoided potential inaccuracies with store opening/closing times.

11. **(Addressed and Implemented)**  
    - Composite keys removed.

12. **(No Plans For Implementation)**  
    - Initial plans dropped due to scope changes.

---

### Suggested Endpoints
1. **(No Plans For Implementation)**  
   - Out of scope to manage payments; focus remains on optimizations.

2. **(Addressed and Implemented)**  
   - Similar functionality added to the `Optimize Shopping Route` endpoint.

---

## Russel Ferrel

### Code Review Comments
1. **(Addressed and Implemented)**  
   - Same as Aiden King’s Code Review #9.

2. **(Addressed and Implemented)**  
   - Same as Megan Fung’s Code Review #3.

3. **(Addressed and Implemented)**  
   - Overhauled error handling.

4. **(Addressed and Implemented)**  
   - Capitalization consistency fixed in class names.

5. **(Addressed and Implemented)**  
   - Same as Megan Fung’s Code Review #2.

6. **(Addressed and Implemented)**  
   - Same as Megan Fung’s Code Review #1.

7. **(Addressed and Implemented)**  
   - Overhauled error handling.

8. **(Addressed and Implemented)**  
   - List comprehension will be used when deemed more appropriate than `for` loops. Will not use for every instance of a for loop as suggested, but will consider and use when it would make code more clear.

9. **(Addressed and Implemented)**  
   - Standardized query code in functions.

10. **(Addressed and Implemented)**  
    - Store location added to `Store` class.

11. **(No Plans For Implementation)**  
    - Same as Megan Fung’s Code Review #12.

12. **(Addressed and Implemented)**  
    - Same as Aiden King’s Code Review #12.

---

### Schema/API Design
1. **(Addressed and Implemented)**  
   - Same as Aiden King’s Schema/API Design #9.

2. **(Addressed and Implemented)**  
   - Updated data for unique locations.

3. **(Addressed and Implemented)**  
   - Same as Aiden King’s Schema/API Design #1.

4. **(Addressed and Implemented)**  
   - Same as above (#2).

5. **(No Plans For Implementation)**  
   - Made store names non-nullable instead.

6. **(Addressed and Implemented)**  
   - Same as Aiden King’s Schema/API Design #9.

7. **(Addressed and Implemented)**  
   - Same as Aiden King’s Code Review #2.

8. **(No Plans For Implementation)**  
   - User location stored upon creation.

9. **(Addressed and Implemented)**  
   - API spec clarified (e.g., list name definition).

10. **(Addressed and Implemented)**  
    - Fixed commas in API spec.

11. **(Addressed and Implemented)**  
    - Clarified storage format for monetary values (in cents).

12. **(Addressed and Implemented)**  
    - IDs standardized to `bigint`.

13. **(Addressed and Implemented)**  
    - Internal server error fixed.

---

### Suggested Endpoints
1. **(No Plans For Implementation)**  
   - Payments are out of scope; focus remains on optimization.

2. **(Addressed and Implemented)**  
   - Integrated into the `Optimize Shopping Route` endpoint.
