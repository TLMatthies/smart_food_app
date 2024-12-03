from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import auth, stores, users, shopping
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

description = """
Hungry? Tight on cash? Both? The Crusty Cart has you covered. With our state-of-the-art database technology, we can find you the food you need at a price you can afford. With the Crusty Cart, you can create robust shopping lists, learn their nutritional value, and find the stores in the Calpoly area that will fulfill your shopping needs in the way that's right for you.!
"""

app = FastAPI(
    title="Smart Food App",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Timothy Matthies",
        "email": "tmatthie@calpoly.edu",
        "name": "Aiden Rodriguez",
        "email": "arodr474@calpoly.edu",
        "name": "Kevin Rutledge",
        "email": "krutledg@calpoly.edu",
        "name": "McCay Ruddick",
        "email": "mruddick@calpoly.edu",
    },
)

# Add middleware if or when applicable
# origins = ["http://localhost:3000"]  # Frontend url
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include routers
app.include_router(users.router)
app.include_router(stores.router)
app.include_router(shopping.router)

@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")
    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to the Smart Food App API"}