from fastapi import APIRouter, HTTPException, Path, Depends
import app.models 
from app.models import User
from app.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from typing import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.auth import get_current_user, bcrypt_context


router = APIRouter(prefix="/users", tags=['users'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(get_current_user)]


class CreateUserRequest(BaseModel):
    username:str
    first_name:str
    last_name:str
    password: str
    role: str = "user"


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user( db:db_dependency, create_user_request:CreateUserRequest):
    user_model = User(
        username = create_user_request.username,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        role = create_user_request.role
    )
    db.add(user_model)
    db.commit()

@router.put("/update", status_code=status.HTTP_200_OK)
async def update_user(user:user_dependancy, db:db_dependency, create_user_request:CreateUserRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    user_model = db.query(User).filter(user['id'] == User.id).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    
    user_model.first_name = create_user_request.first_name
    user_model.last_name = create_user_request.last_name
    user_model.role = create_user_request.role
    user_model.hashed_password = bcrypt_context.hash(create_user_request.password)
    db.add(user_model)
    db.commit()   
    db.refresh(user_model)

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user:user_dependancy,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    user_model = db.query(User).filter(user['id'] == User.id).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    db.delete(user_model)
    db.commit()


