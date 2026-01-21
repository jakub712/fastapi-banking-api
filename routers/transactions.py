from fastapi import HTTPException, Path, Depends, APIRouter
from app.models import Transaction, User, Account
from app.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from app.auth import get_current_user


router = APIRouter(prefix='/transactions', tags=['tranactions'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(get_current_user)]


class Transfer_Request(BaseModel):
    amount_pence: int = Field(gt=0)

class Deposit_Request(BaseModel):
    amount_pence: int = Field(gt=0)

class Withdraw_Request(BaseModel):
    amount_pence: int = Field(gt=0)


@router.post("/deposit", status_code=status.HTTP_200_OK)
async def deposit_money(user: user_dependancy, db: db_dependency, deposit_request: Deposit_Request):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    account = db.query(Account).filter(Account.user_id == User.id).first()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    account.balance_pence += deposit_request.amount_pence
    tx = Transaction(
        from_account_id = None,
        to_account_id = account.id,
        amount_pence = deposit_request.amount_pence,
        status = 'Completed',
        user_id = user['id']
    )
    db.add(tx)

    db.commit()
    db.refresh(account)
    return {'message': f'Successfully deposited {deposit_request.amount_pence/100:.2f}, your new balance is {account.balance_pence/100:.2f}'}

@router.post("/withdraw", status_code=status.HTTP_200_OK)
async def withdraw_money(user: user_dependancy, db:db_dependency, withdraw_request:Withdraw_Request):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    account = db.query(Account).filter(Account.user_id == User.id).first()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    if account.balance_pence < withdraw_request.amount_pence:
        raise HTTPException(status_code=400, detail='not enough funds to process withdrawl')
    account.balance_pence -= withdraw_request.amount_pence
    tx = Transaction(
        from_account_id = account.id,
        to_account_id = None,
        amount_pence = withdraw_request.amount_pence,
        status = 'completed',
        user_id = user['id']
    )
    db.add(tx)

    db.commit()
    db.refresh(account)
    return{'messege':f'Successfully withdrawn {withdraw_request.amount_pence/100:.2f}, your new balance is {account.balance_pence/100:.2f}'}

@router.post("/transfer/{user_id}", status_code=status.HTTP_200_OK)
async def transfer_money(user: user_dependancy, db:db_dependency, transfer_request:Transfer_Request, user_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    sender_account = db.query(Account).filter(Account.user_id == User.id).first()
    resiver_account = db.query(Account).filter(Account.user_id == user_id) .first()
    if sender_account is None or resiver_account is None:
        raise HTTPException(status_code=404, detail='bank account does not exsist')
    if sender_account.balance_pence < transfer_request.amount_pence:
        raise HTTPException(status_code=400, detail='not enough funds to process transaction')
    sender_account.balance_pence = sender_account.balance_pence - transfer_request.amount_pence
    resiver_account.balance_pence = transfer_request.amount_pence + resiver_account.balance_pence
    tx = Transaction(
        from_account_id = sender_account.id,
        to_account_id = resiver_account.user_id,
        amount_pence = transfer_request.amount_pence,
        status = 'complete',
        user_id = sender_account.id
    )
    db.add(tx)

    db.commit()
    db.refresh(sender_account)
    db.refresh(resiver_account)
    return {'message': f'Successfully sent money your new balance is {sender_account.balance_pence/100:.2f}'}


@router.get("/all", status_code=status.HTTP_200_OK)
async def all_transactions_for_user(user: user_dependancy,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='authentication failed')
    account = db.query(Account).filter(Account.user_id == User.id).first()
    if account is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='account not found')
    outgoing_transactions = db.query(Transaction).filter(Transaction.from_account_id == account.id).all()
    incoming_transactions = db.query(Transaction).filter(Transaction.to_account_id == account.id).all()
    return outgoing_transactions + incoming_transactions
