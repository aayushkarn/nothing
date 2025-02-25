from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(255), unique=True, index=True, nullable=True)
    password = Column(String(255))
    business_name = Column(String(255), nullable=False)
    business_ein = Column(String(255), nullable=False)
    is_verified = Column(Integer, default=0)
    verification_code = Column(Integer, nullable=True)
    verification_sent_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())