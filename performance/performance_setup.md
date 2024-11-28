# Setting Up Performance Testing Environment

## Prerequisites
- Docker installed

## Setup Steps
In your terminal, navigate to the performance directory:
```bash
cd performance
```

Create .env file:
```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=perf_db
POSTGRES_PORT=5432
POSTGRES_URI="postgresql://postgres:postgres@perf_db:5432/perf_db"
```

Start containers:
```bash
docker-compose up -d
```

Generate test data:
```bash
docker-compose exec datagen python generate_data.py
```

To run test queries:
```bash
docker-compose exec perf_db psql -U postgres -d perf_db
```

To reset environment:
```bash
docker-compose down -v
```

## Database Contents After Generation
- Users: 100,000 rows
- Stores: 100 rows
- Food Items: ~5,000 rows
- Catalog Items: 100,000 rows
- Shopping Lists: ~200,000 rows
- Shopping List Items: ~600,000 rows
- Total: ~1 million rows