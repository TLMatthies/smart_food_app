from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from src.api import auth, catalogs, stores, users
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

description = """
TODO: McCay can come up with a better project description
Smart Food App helps users optimize their grocery shopping by finding the best deals
and managing their food shopping needs.
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
app.include_router(catalogs.router)

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