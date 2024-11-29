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

### Build the datagen Service
Before starting the containers, build the datagen service. Ensure any changes to generate_data.py or init.sql are included:
```bash
docker-compose build --no-cache datagen
```

### Start containers
If this is your first time setting up, start the containers:
```bash
docker-compose up -d
```
**Note**: If you have previously started the containers and the database was initialized without the necessary extensions, you need to stop the containers and remove the volumes to re-initialize the database with the extensions:

```bash
docker-compose down -v
docker-compose up -d
```

### Generate test data
Run the data generation script:
```bash
docker-compose exec datagen python generate_data.py
```

### To run test queries
Connect to PostgreSQL database to run test queries:
```bash
docker-compose exec perf_db psql -U postgres -d perf_db
```

### To reset environment
To reset the environment and remove all data:
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