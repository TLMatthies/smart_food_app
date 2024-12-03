# Query Performance Analysis

## Introduction
This details our approach to performance optimization of the The Crusty Cart's database which follows the procedure of measure → tune → measure. We focused on queries that showed significant room for improvement and avoided over-optimization where performance was already adequate.

## Significant Optimizations

### 1. Store Catalog Query
**Endpoint**: `/stores/{store_id}/catalog`

### Explain query
```sql
EXPLAIN ANALYZE
SELECT food_item.food_id, name, quantity, price
FROM catalog_item
JOIN catalog ON catalog_item.catalog_id = catalog.catalog_id
JOIN food_item ON catalog_item.food_id = food_item.food_id
WHERE catalog.store_id = 1;
```

#### Initial Performance
```sql
 Hash Join  (cost=172.67..2085.92 rows=1000 width=37) (actual time=0.772..8.340 rows=1000 loops=1)
   Hash Cond: (catalog_item.food_id = food_item.food_id)
   ->  Hash Join  (cost=2.26..1912.89 rows=1000 width=12) (actual time=0.023..7.481 rows=1000 loops=1)
         Hash Cond: (catalog_item.catalog_id = catalog.catalog_id)
         ->  Seq Scan on catalog_item  (cost=0.00..1637.00 rows=100000 width=16) (actual time=0.002..3.157 rows=100000 loops=1)
         ->  Hash  (cost=2.25..2.25 rows=1 width=4) (actual time=0.011..0.012 rows=1 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 9kB
               ->  Seq Scan on catalog  (cost=0.00..2.25 rows=1 width=4) (actual time=0.003..0.007 rows=1 loops=1)
                     Filter: (store_id = 1)
                     Rows Removed by Filter: 99
   ->  Hash  (cost=107.96..107.96 rows=4996 width=29) (actual time=0.729..0.729 rows=4996 loops=1)
         Buckets: 8192  Batches: 1  Memory Usage: 365kB
         ->  Seq Scan on food_item  (cost=0.00..107.96 rows=4996 width=29) (actual time=0.002..0.311 rows=4996 loops=1)
 Planning Time: 0.556 ms
 Execution Time: 8.389 ms
```
Initial execution time: 8.389ms

#### Analysis
- Sequential scan on catalog_item processing 100,000 rows
- Multiple hash joins without proper index support
- Unnecessary full table scan for catalog items

#### Optimization Applied
```sql
CREATE INDEX idx_catalog_item_catalog ON catalog_item(catalog_id);
```

#### Improved Performance
```sql
 Hash Join  (cost=170.70..217.08 rows=1000 width=37) (actual time=0.692..0.939 rows=1000 loops=1)
   Hash Cond: (catalog_item.food_id = food_item.food_id)
   ->  Nested Loop  (cost=0.29..44.04 rows=1000 width=12) (actual time=0.022..0.154 rows=1000 loops=1)
         ->  Seq Scan on catalog  (cost=0.00..2.25 rows=1 width=4) (actual time=0.004..0.009 rows=1 loops=1)
               Filter: (store_id = 1)
               Rows Removed by Filter: 99
         ->  Index Scan using idx_catalog_item_catalog on catalog_item  (cost=0.29..31.79 rows=1000 width=16) (actual time=0.016..0.078 rows=1000 loops=1)
               Index Cond: (catalog_id = catalog.catalog_id)
   ->  Hash  (cost=107.96..107.96 rows=4996 width=29) (actual time=0.664..0.664 rows=4996 loops=1)
         Buckets: 8192  Batches: 1  Memory Usage: 365kB
         ->  Seq Scan on food_item  (cost=0.00..107.96 rows=4996 width=29) (actual time=0.002..0.330 rows=4996 loops=1)
 Planning Time: 0.254 ms
 Execution Time: 0.972 ms
```
Final execution time: 0.972ms

**Improvement**: 88% reduction in execution time
- Eliminated full table scan
- Enabled efficient index scan on catalog_item
- Reduced data processing overhead

### 2. User Shopping Lists Query
**Endpoint**: `/users/{user_id}/lists`

### Explain query
```sql
EXPLAIN ANALYZE
SELECT list_id, name
FROM shopping_list
WHERE user_id = 1;
```

#### Initial Performance
```sql
 Seq Scan on shopping_list  (cost=0.00..3776.64 rows=3 width=13) (actual time=0.005..10.210 rows=2 loops=1)
   Filter: (user_id = 1)
   Rows Removed by Filter: 200129
 Planning Time: 0.066 ms
 Execution Time: 10.218 ms
```
Initial execution time: 10.218ms

#### Analysis
- Full table scan processing over 200,000 rows
- Filtering after reading entire table
- High number of rejected rows (200,129)

#### Optimization Applied
```sql
CREATE INDEX idx_shopping_list_user ON shopping_list(user_id);
```

#### Improved Performance
```sql
 Index Scan using idx_shopping_list_user on shopping_list  (cost=0.42..8.47 rows=3 width=13) (actual time=0.020..0.021 rows=2 loops=1)
   Index Cond: (user_id = 1)
 Planning Time: 0.125 ms
 Execution Time: 0.030 ms
```
Final execution time: 0.030ms

**Improvement**: 99.7% reduction in execution time
- Eliminated full table scan
- Direct index lookup for user's lists
- Dramatic reduction in processed rows

### 3. Route Optimization Query
**Endpoint**: `/shopping/route_optimize`

### Explain query
```sql
EXPLAIN ANALYZE
WITH they_got_it AS (
    SELECT 
        food_item.name AS item,
        store.name AS store_name, 
        store.store_id AS store_id,
        catalog_item.price AS price,
        ROUND((earth_distance(
            ll_to_earth(store.latitude, store.longitude), 
            ll_to_earth((SELECT latitude FROM users WHERE users.user_id = 1), 
                        (SELECT longitude FROM users WHERE users.user_id = 1))
        ) / 1000)::NUMERIC, 1)::FLOAT AS distance
    FROM store
    JOIN catalog ON catalog.store_id = store.store_id
    JOIN catalog_item ON catalog.catalog_id = catalog_item.catalog_id
    JOIN food_item ON food_item.food_id = catalog_item.food_id
    WHERE food_item.food_id IN (
        SELECT food_id
        FROM shopping_list_item
        WHERE list_id = 1
        )
        AND price < 1000
    ORDER BY item, price, distance
)
SELECT * FROM they_got_it
WHERE distance < 10;
```


#### Initial Performance
```sql
 Sort  (cost=2293.81..2293.87 rows=25 width=60) (actual time=11.200..11.205 rows=39 loops=1)
   Sort Key: food_item.name, catalog_item.price, ((round(((sec_to_gc(cube_distance((ll_to_earth(store.latitude, store.longitude))::cube, (ll_to_earth($0, $1))::cube)) / '1000'::double precision))::numeric, 1))::double precision)
   Sort Method: quicksort  Memory: 28kB
   InitPlan 1 (returns $0)
     ->  Index Scan using user_pkey on users  (cost=0.29..8.31 rows=1 width=8) (actual time=0.005..0.006 rows=1 loops=1)
           Index Cond: (user_id = 1)
   InitPlan 2 (returns $1)
     ->  Index Scan using user_pkey on users users_1  (cost=0.29..8.31 rows=1 width=8) (actual time=0.003..0.004 rows=1 loops=1)
           Index Cond: (user_id = 1)
   InitPlan 3 (returns $2)
     ->  Index Scan using user_pkey on users users_2  (cost=0.29..8.31 rows=1 width=8) (actual time=0.011..0.011 rows=1 loops=1)
           Index Cond: (user_id = 1)
   InitPlan 4 (returns $3)
     ->  Index Scan using user_pkey on users users_3  (cost=0.29..8.31 rows=1 width=8) (actual time=0.001..0.001 rows=1 loops=1)
           Index Cond: (user_id = 1)
   ->  Nested Loop  (cost=5.11..2259.99 rows=25 width=60) (actual time=0.649..11.160 rows=39 loops=1)
         ->  Nested Loop  (cost=4.83..2233.35 rows=25 width=55) (actual time=0.513..10.704 rows=39 loops=1)
               ->  Nested Loop  (cost=4.69..2151.77 rows=76 width=16) (actual time=0.134..9.432 rows=126 loops=1)
                     ->  Hash Join  (cost=4.54..2139.62 rows=76 width=16) (actual time=0.130..9.340 rows=126 loops=1)
                           Hash Cond: (catalog_item.food_id = shopping_list_item.food_id)
                           ->  Seq Scan on catalog_item  (cost=0.00..1887.00 rows=94416 width=12) (actual time=0.003..5.947 rows=94596 loops=1)
                           ->  Seq Scan on catalog_item  (cost=0.00..1887.00 rows=94416 width=12) (actual time=0.003..5.947 rows=94596 loops=1)
                                 Filter: (price < 1000)
                                 Rows Removed by Filter: 5404
                           ->  Hash  (cost=4.50..4.50 rows=4 width=4) (actual time=0.028..0.029 rows=7 loops=1)
                                 Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                 ->  Index Only Scan using shopping_list_item_pkey on shopping_list_item  (cost=0.42..4.50 rows=4 width=4) (actual time=0.023..0.024 rows=7 loops=1)
                                       Index Cond: (list_id = 1)
                                       Heap Fetches: 0
                     ->  Index Scan using catalog_pkey on catalog  (cost=0.14..0.16 rows=1 width=8) (actual time=0.000..0.000 rows=1 loops=126)
                           Index Cond: (catalog_id = catalog_item.catalog_id)
               ->  Index Scan using store_pkey on store  (cost=0.14..1.08 rows=1 width=43) (actual time=0.010..0.010 rows=0 loops=126)
                     Index Cond: (store_id = catalog.store_id)
                     Filter: ((round(((sec_to_gc(cube_distance((ll_to_earth(latitude, longitude))::cube, (ll_to_earth($2, $3))::cube)) / '1000'::double precision))::numeric, 1))::double precision < '10'::double precision)
                     Rows Removed by Filter: 1
         ->  Index Scan using food_item_pkey on food_item  (cost=0.28..0.30 rows=1 width=29) (actual time=0.001..0.001 rows=1 loops=39)
               Index Cond: (food_id = catalog_item.food_id)
 Planning Time: 1.217 ms
 Execution Time: 11.536 ms
```
Initial execution time: 11.536ms

#### Analysis
- Sequential scan on catalog_item
- Multiple joins without proper indexing
- Processing large number of rows

#### Optimization Applied
```sql
CREATE INDEX idx_catalog_item_composite ON catalog_item(food_id, price);
```

#### Improved Performance
```sql
 Sort  (cost=181.24..181.30 rows=25 width=60) (actual time=1.630..1.632 rows=39 loops=1)
   Sort Key: food_item.name, catalog_item.price, ((round(((sec_to_gc(cube_distance((ll_to_earth(store.latitude, store.longitude))::cube, (ll_to_earth($0, $1))::cube)) / '1000'::double precision))::numeric, 1))::double precision)
   Sort Method: quicksort  Memory: 28kB
   InitPlan 1 (returns $0)
     ->  Index Scan using user_pkey on users  (cost=0.29..8.31 rows=1 width=8) (actual time=0.003..0.003 rows=1 loops=1)
           Index Cond: (user_id = 1)
   InitPlan 2 (returns $1)
     ->  Index Scan using user_pkey on users users_1  (cost=0.29..8.31 rows=1 width=8) (actual time=0.003..0.003 rows=1 loops=1)
           Index Cond: (user_id = 1)
   InitPlan 3 (returns $2)
     ->  Index Scan using user_pkey on users users_2  (cost=0.29..8.31 rows=1 width=8) (actual time=0.010..0.010 rows=1 loops=1)
           Index Cond: (user_id = 1)
   InitPlan 4 (returns $3)
     ->  Index Scan using user_pkey on users users_3  (cost=0.29..8.31 rows=1 width=8) (actual time=0.001..0.001 rows=1 loops=1)
           Index Cond: (user_id = 1)
   ->  Hash Join  (cost=48.48..147.42 rows=25 width=60) (actual time=0.649..1.600 rows=39 loops=1)
         Hash Cond: (store.store_id = catalog.store_id)
         ->  Seq Scan on store  (cost=0.00..79.50 rows=33 width=43) (actual time=0.269..0.951 rows=28 loops=1)
               Filter: ((round(((sec_to_gc(cube_distance((ll_to_earth(latitude, longitude))::cube, (ll_to_earth($2, $3))::cube)) / '1000'::double precision))::numeric, 1))::double precision < '10'::double precision)
               Rows Removed by Filter: 72
         ->  Hash  (cost=47.53..47.53 rows=76 width=29) (actual time=0.238..0.238 rows=126 loops=1)
               Buckets: 1024  Batches: 1  Memory Usage: 16kB
               ->  Hash Join  (cost=4.25..47.53 rows=76 width=29) (actual time=0.064..0.225 rows=126 loops=1)
                     Hash Cond: (catalog_item.catalog_id = catalog.catalog_id)
                     ->  Nested Loop  (cost=1.00..44.07 rows=76 width=29) (actual time=0.044..0.191 rows=126 loops=1)
                           ->  Nested Loop  (cost=0.71..37.70 rows=4 width=33) (actual time=0.028..0.050 rows=7 loops=1)
                                 ->  Index Only Scan using shopping_list_item_pkey on shopping_list_item  (cost=0.42..4.50 rows=4 width=4) (actual time=0.020..0.021 rows=7 loops=1)
                                       Index Cond: (list_id = 1)
                                       Heap Fetches: 0
                                 ->  Index Scan using food_item_pkey on food_item  (cost=0.28..8.30 rows=1 width=29) (actual time=0.004..0.004 rows=1 loops=7)
                                       Index Cond: (food_id = shopping_list_item.food_id)
                           ->  Index Scan using idx_catalog_item_composite on catalog_item  (cost=0.29..1.40 rows=19 width=12) (actual time=0.007..0.019 rows=18 loops=7)
                                 Index Cond: ((food_id = food_item.food_id) AND (price < 1000))
                     ->  Hash  (cost=2.00..2.00 rows=100 width=8) (actual time=0.017..0.017 rows=100 loops=1)
                           Buckets: 1024  Batches: 1  Memory Usage: 12kB
                           ->  Seq Scan on catalog  (cost=0.00..2.00 rows=100 width=8) (actual time=0.002..0.007 rows=100 loops=1)
 Planning Time: 1.299 ms
 Execution Time: 1.953 ms
```
Final execution time: 1.953ms

**Improvement**: 83% reduction in execution time
- Enabled efficient filtering on both food_id and price
- Reduced processed rows significantly
- Improved join performance

## Other Queries
Several other queries were analyzed but showed already-optimal performance:

1. **Shopping List Details Query** (0.066ms)
   - Already using efficient index scans
   - No optimization needed

2. **List Nutritional Facts Query** (0.164ms)
   - Utilizing proper indexes
   - Sub-millisecond performance

3. **Price Comparison Query** (0.143ms)
   - Efficient use of indexes and window functions
   - Already optimized execution plan

## Conclusion
We identified and optimized the most critical performance bottlenecks while avoiding unnecessary optimization of already-efficient queries. The most significant improvements came from eliminating full table scans on large tables and optimizing join conditions with proper indexes.