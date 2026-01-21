from fastapi import FastAPI
import app.models as models
from app.database import engine
from routers import accounts, transactions, users
from app import auth

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(bind=engine)


app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(users.router)
app.include_router(auth.router)

