#accounts.py
from fastapi import HTTPException, Path, Depends, APIRouter
import app.models
from app.models import Account, User
from app.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from app.auth import get_current_user, bcrypt_context


router = APIRouter(prefix='/accounts', tags=['accounts'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(get_current_user)]


@router.post("/create/{user_id}", status_code=status.HTTP_201_CREATED)
def create_account(user:user_dependancy,user_id: int, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    user_model = db.query(User).filter(User.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='user not found')
    account = Account(
        user_id = user["id"],
        balance = 0,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return{
        'account_id': account.id,
        'user_id':account.user_id,
        'balance': account.balance,
        'account_type': account
    }

@router.get("/get_user/{user_name}", status_code=status.HTTP_200_OK)
async def get_user(user:user_dependancy, db:db_dependency, user_name:str):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    user_model = db.query(User).filter(User.username == user_name).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='user not found')
    account = db.query(Account).filter(Account.user_id == user['id']).first()
    if account is None:
        raise HTTPException(status_code=404, detail='account not found')
    return{
        'account_id':account.id,
        'user_id':account.user_id,
        'balance':account.balance,
    }