### Route Optimization Quantity Race
**Issue:** Store inventory becomes unavailable during route calculation
```python
@router.post("/route-optimize")
def optimize_shopping_route(user_id: int, food_id: int, use_preferences: bool):
    # First read shows item in stock
    # Store updates quantity to 0
    # User gets directed to store with no stock
```
**Solution:** We will use REPEATABLE READ isolation to ensure quantity stays consistent during the entire route calculation.

### Price Comparison Race
**Issue:** Store prices change during comparison
```python
@router.post("/compare-prices")
def compare_prices(request: PricesRequest):
    # Read price from Store 1 = $10
    # Store 2 changes price $15 -> $8
    # Read price from Store 2 = $8
    # Incorrect comparison results
```
**Solution:** We will use REPEATABLE READ isolation so all price reads within the transaction see the same snapshot of data.

### Budget-Based Route Optimization
**Issue:** Prices change during route calculation, violating budget constraints
```python
@router.post("/route-optimize")
def optimize_shopping_route(user_id: int, food_id: int, use_preferences: bool):
    # Check budget = $10
    # Store changes price $8 -> $12
    # Recommend store that's now over budget
```
**Solution:** We will use SERIALIZABLE isolation since we're making financial decisions based on multiple price points.

### Shopping List Budget Validation
**Issue:** Prices increase after list creation
```python
@router.post("/{user_id}/lists/{list_id}")
def add_item_to_list(list_id: int, user_id: int, items: list[item]):
    # Create list with total = $40
    # Store increases prices 15%
    # List now exceeds user's budget
```
**Solution:** We will use REPEATABLE READ isolation during list creation to ensure consistent price checks.

## Implementation

Add the appropriate isolation level to each transaction:
```python
with engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
    with conn.begin():
        # ...
```

For budget-critical operations:
```python
with engine.connect().execution_options(isolation_level="SERIALIZABLE") as conn:
    with conn.begin():
        # ...
```