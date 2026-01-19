from fastapi import FastAPI, HTTPException, Path, Depends
import app.models as models
from app.models import Bank_Account
from app.database import SessionLocal, engine
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class AccountRequest(BaseModel):
    first_name: str
    last_name: str
    balance: int

class Transfer_Request(BaseModel):
    amount: float = Field(gt=0)

class Top_Up_Request(BaseModel):
    amount: float = Field(gt=0)

class Withdraw_Request(BaseModel):
    amount: float = Field(gt=0)

@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Bank_Account).all()

@app.post("/bank/top_up/{bank_id}", status_code=status.HTTP_202_ACCEPTED)
async def top_up(db: db_dependency, top_up_request: Top_Up_Request, bank_id: int = Path(gt=0)):
    user = db.query(Bank_Account).filter(Bank_Account.id == bank_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='id not found')
    user.balance += top_up_request.amount
    db.commit()
    db.refresh(user)
    return {'message': f'Successfully added {top_up_request.amount}, your new balance is {user.balance}'}

@app.post("/bank/withdraw/{bank_id}", status_code=status.HTTP_200_OK)
async def withdraw_money(db: db_dependency, withdraw_request: Withdraw_Request, bank_id: int = Path(gt=0)):
    user = db.query(Bank_Account).filter(Bank_Account.id == bank_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='bank id does not exist')
    if user.balance < withdraw_request.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='not enough funds')
    user.balance = user.balance - withdraw_request.amount
    db.commit()
    db.refresh(user)
    return {'message': f'Successfully withdrawn {withdraw_request.amount}, your new balance is {user.balance}'}

@app.get("/bank/{bank_id}", status_code=status.HTTP_200_OK)
async def get_user(db: db_dependency, bank_id: int = Path(gt=0)):
    bank_model = db.query(Bank_Account).filter(Bank_Account.id == bank_id).first()
    if bank_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='id does not exist')
    return bank_model

@app.post("/bank", status_code=status.HTTP_201_CREATED)
async def create_account(db: db_dependency, bank_request: AccountRequest):
    bank_model = Bank_Account(**bank_request.model_dump())
    db.add(bank_model)
    db.commit()

@app.put("/bank/{bank_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_account(db: db_dependency, bank_request: AccountRequest, bank_id: int = Path(gt=0)):
    bank_model = db.query(Bank_Account).filter(Bank_Account.id == bank_id).first()
    if bank_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='id does not exist')
    bank_model.first_name = bank_request.first_name
    bank_model.last_name = bank_request.last_name
    bank_model.balance = bank_request.balance
    db.add(bank_model)
    db.commit()

@app.delete("/bank/{bank_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(db: db_dependency, bank_id: int = Path(gt=0)):
    bank_model = db.query(Bank_Account).filter(Bank_Account.id == bank_id).first()
    if bank_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='id does not exist')
    db.query(Bank_Account).filter(Bank_Account.id == bank_id).delete()
    db.commit()

@app.post("/bank/{bank_id1}/{bank_id2}", status_code=status.HTTP_200_OK)
async def transfer_money(db: db_dependency, transfer_request: Transfer_Request, bank_id1: int = Path(gt=0), bank_id2: int = Path(gt=0)):
    user_1 = db.query(Bank_Account).filter(Bank_Account.id == bank_id1).first()
    user_2 = db.query(Bank_Account).filter(Bank_Account.id == bank_id2).first()
    if user_1 is None or user_2 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='account does not exist')
    if user_1.balance < transfer_request.amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='not enough money')
    user_1.balance = user_1.balance - transfer_request.amount
    user_2.balance = transfer_request.amount + user_2.balance
    db.commit()
    db.refresh(user_1)
    db.refresh(user_2)
    return {'message': f'Successfully sent money your new balance is {user_1.balance}'}




###------------------------------------------------------------------------------------
@router.get("/")
async def list_all_transactions(db:db_dependency):
    return db.query(Transaction).all()