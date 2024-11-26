# Performance Testing Documentation

## Fake Data Modeling
- Generated using generate_data.py
- Total rows:
  - Users: 100,000
  - Stores: 100
  - Food Items: 4,996
  - Catalog Items: 100,000
  - Shopping Lists: 201,204
  - Shopping List Items: 613,730
- Total: ~1,020,030 rows

Justification: Modeling real-world ratios where:
- Each user has ~2 shopping lists
- Each list has ~3 items
- Each store carries ~1000 items
- 100 stores is realistic for a city deployment

## Initial Performance Testing
Test all endpoints and measure execution time:

```sql
EXPLAIN ANALYZE
SELECT sl.list_id, sl.name, fi.name as item_name, sli.quantity
FROM shopping_list sl
JOIN shopping_list_item sli ON sl.list_id = sli.list_id
JOIN food_item fi ON sli.food_id = fi.food_id
WHERE sl.user_id = 1
ORDER BY sl.list_id DESC;

EXPLAIN ANALYZE
SELECT catalog_item_id as item_sku, name, quantity, price
FROM catalog_item
JOIN catalog ON catalog_item.catalog_id = catalog.catalog_id
JOIN food_item fi ON catalog_item.food_id = fi.food_id
WHERE catalog.store_id = 1;

EXPLAIN ANALYZE
SELECT s.store_id, s.name, s.latitude, s.longitude, ci.price
FROM store s
JOIN catalog c ON c.store_id = s.store_id
JOIN catalog_item ci ON ci.catalog_id = c.catalog_id
WHERE ci.food_id = 1
ORDER BY ci.price ASC;
```

Initial Results:
1. Shopping History Query: 24.840ms
2. Store Catalog Query: 24.230ms
3. Route Optimization Query: 9.679ms

## Performance Analysis & Optimization

### Shopping History Query (24.840ms → 0.506ms)
Initial EXPLAIN output:
```sql
Gather Merge (cost=3694.58..3695.16 rows=5 width=37) (actual time=22.143..24.785 rows=5 loops=1)
...
```
Problem: Full table scan on shopping_list

Solution:
```sql
CREATE INDEX idx_shopping_list_user_id ON shopping_list(user_id, list_id DESC);
CREATE INDEX idx_shopping_list_item_composite ON shopping_list_item(list_id, food_id);
```

### Store Catalog Query (24.230ms → 2.135ms)
Initial EXPLAIN output:
```sql
Hash Join (cost=172.67..2085.92 rows=1000 width=33) (actual time=1.872..24.145 rows=1000 loops=1)
...
```
Problem: Sequential scans on catalog_item and food_item

Solution:
```sql
CREATE INDEX idx_catalog_item_store ON catalog_item(catalog_id, food_id) 
INCLUDE (catalog_item_id, quantity, price);
```

### Route Optimization Query (9.679ms → 0.878ms)
Initial EXPLAIN output:
```sql
Sort (cost=1897.78..1898.00 rows=87 width=47) (actual time=9.553..9.563 rows=100 loops=1)
...
```
Problem: Sequential scan on catalog_item when filtering by food_id

Solution:
```sql
CREATE INDEX idx_catalog_item_food_price ON catalog_item(food_id, price);
```
