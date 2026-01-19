#auth.py
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from app.models import User, Transaction
from app.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone


router = APIRouter(prefix='/auth', tags = ['auth'])

SECERET_KEY = '3431cbf6ab049aa7b227295c9c3192601715f5071b8428b5fcbcb7f5d3e27434'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class Token(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[Session, Depends(get_db)]


def authenticate_user(username:str, password:str, db):
    users = db.query(User).filter(User.username == username).first()
    if not users:
        return False
    if not bcrypt_context.verify(password, users.hashed_password):
        return False
    return users

def create_access_token(username:str, user_id:int, role: str, expires_delta:timedelta):
    encode = {'sub':username, 'id':user_id, 'role':role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECERET_KEY, algorithm=ALGORITHM)
async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECERET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get('sub')
        user_id:int = payload.get('id')
        user_role:str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong credentials')
        return{'username':username, 'id':user_id, 'user_role':user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong credentials')
    
user_dependancy = Annotated[dict, Depends(get_current_user)]

    
@router.post("/token", include_in_schema=False, response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependancy):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='wrong credentials')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return{'access_token':token, 'token_type':'bearer'}

@router.post("/create_admin",status_code=status.HTTP_200_OK)
async def create_admin(db:db_dependancy, user:user_dependancy):
    admins =  db.query(User).filter(User.role == 'admin').count()
    if admins > 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='an admin already exsists')
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    
    user_model = db.query(User).filter(User.id == user['id']).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='user does not exsist')
    user_model.role = 'admin'
    db.commit()
    return {'messege':f'{user_model.username} has been promoted to admin'}

@router.post("/promote/{user_id}", status_code=status.HTTP_200_OK)
async def promote_to_admin_invite(db:db_dependancy, user:user_dependancy, user_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    user_model = db.query(User).filter(User.id == user['id']).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail='user does not exsist')
    if user_model.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='only an admin can promote others')

    user_model2 = db.query(User).filter(User.id == user_id).first()
    if user_model2 is None:
        raise HTTPException(status_code=404, detail='user does not exsist')
    user_model2.role = 'admin'
    db.commit()
    return {'messege':f'{user_model2.username} has been promoted to admin'}

@router.get("/all_users", status_code= status.HTTP_200_OK)
async def read_all_users(db:db_dependancy, user:user_dependancy):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    user_model = db.query(User).filter(User.id == user['id']).first()
    if user_model.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='only an admin can access this data')
    all_users = db.query(User).all()
    return all_users

#@router.get ("/all_accounts", status_code=status.HTTP_200_OK)
#async def read_all_accounts

@router.get("/all_transactions", status_code=status.HTTP_200_OK)
async def read_all_transactions(db:db_dependancy, user:user_dependancy):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    user_model = db.query(User).filter(User.id == user['id']).first()
    if user_model.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='only an admin can access this data')
    all_transactions = db.query(Transaction).all()
    return all_transactions





#Things an admin can do
#view everything read only

#list all accounts(balances, owner, user_id)

#reset user password

#soft delete accounts

#reverse transactions
#mark despitues as flagged


#things to impliment
#audit log (every payment and tranaction)
#add type of accounts
#freezing accounts
#put post get delete