from datetime import datetime
from app.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, Float, Boolean

class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key= True, index= True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)

class Account(Base):
    __tablename__ = "Account"

    id = Column(Integer, primary_key=True, index=True)
    balance_pence = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("User.id"))
    account_type = Column(String)

class Transaction(Base):
    __tablename__ = "Transactions"

    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer)
    to_account_id = Column(Integer)
    amount_pence = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("User.id"))
