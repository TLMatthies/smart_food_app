# Smart Food App - Project Documentation

## Project Overview

This markdown serves as the first step to deploying a working backend API for our app.

## Current Tech Stack

- **FastAPI**: Python web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Supabase**: PostgreSQL database platform
- **Render**: Cloud deployment platform
- **Python 3.11.4**: Primary programming language

## Project Structure

```
smart_food_app/
├── src/
│   ├── api/                  # API endpoints
│   │   ├── server.py         # Main FastAPI application
│   │   ├── auth.py           # Authentication logic
│   │   ├── users.py          # User endpoints
│   │   ├── stores.py         # Store endpoints
│   │   └── catalogs.py       # Catalog endpoints
|   └── database.py           # Database connection
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .gitignore                # Git ignore rules
├── vercel.json               # Vercel deployment config
|── README.md                 # Project readme
│── APISpec.md                # API specification
│── ExampleFlows.md           # Example user flows
└── user_stories.md           # User stories and exceptions
```

## Key Files

- **server.py**: Main application entry point, configures FastAPI and routes
- **auth.py**: Handles API key authentication
- **database.py**: Manages database connection using SQLAlchemy
- **users.py/stores.py/catalogs.py**: Individual endpoint implementations
- **.env**: Contains sensitive configuration (API keys, database URLs)

## Initial Setup Guide

### 1. Local Development Setup

```bash
# Clone the repository
git clone https://github.com/TLMatthies/smart_food_app.git
cd smart_food_app

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Supabase Setup (Database)

1. [Supabase](https://supabase.com/)
2. Create a new project:
   - Choose a name
   - Set a secure database password
   - Choose a region
3. Save the database connection string and credentials
4. Share project access with team members:
   - Go to Project Settings
   - Team & Members
   - Invite us using our Cal Poly email addresses

### 3. Render Setup (Deployment)

1. [Render](https://render.com/)
2. Create a new team:
   - Click profile icon → New Team
   - Name it whatever you want.
   - Invite team members
3. Create a new Web Service:
   - Connect to GitHub repository
   - Configure build settings:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn src.api.server:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `API_KEY`: Your chosen API key
   - `POSTGRES_URI`: Supabase connection string
   - `PYTHON_VERSION`: 3.11.4

### 4. Environment Setup

Create a .env file in your project root:

```
API_KEY=your_chosen_api_key
POSTGRES_URI=postgresql+psycopg2://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

## Database Schema

```sql
-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT
);

-- Stores table
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    open_time TIME NOT NULL,
    close_time TIME NOT NULL
);

-- Food items table
CREATE TABLE food_items (
    food_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    calories INTEGER,
    protein INTEGER,
    total_carbohydrate INTEGER,
    total_sugars INTEGER,
    total_fat INTEGER,
    saturated_fat INTEGER,
    dietary_fiber INTEGER,
    trans_fat INTEGER
);

-- Catalog items table
CREATE TABLE catalog_items (
    catalog_item_id SERIAL PRIMARY KEY,
    store_id INTEGER REFERENCES stores(store_id),
    food_id INTEGER REFERENCES food_items(food_id),
    price INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    UNIQUE(store_id, food_id)
);
```

## Next Steps

### Immediate Tasks

1. **Team Setup**

   - Create Supabase account and project
   - Create Render account and team
   - Share access with team members

2. **Database Implementation**

   - Run schema.sql in Supabase
   - Add initial test data
   - Test database connections

3. **First User Story Implementation**
   - Implement user creation endpoint
   - Implement store listing endpoint
   - Implement catalog viewing endpoint

### Future Enhancements

- Shopping list management
- User preferences system
- Store inventory tracking

## Getting Help

- API Documentation: Visit `/docs` after running the server
- Project Management: GitHub Issues and Projects
- Database Access: Request from Supabase team admin
- Deployment Access: Request from Render team admin

## Contributing

1. Create a new branch for your feature
2. Make changes and test locally
3. Submit a pull request
4. Request review from team members
