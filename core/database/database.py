from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import SQLALCHEMY_DATABASE_URL

# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  


# For PostgreSQL or MySQL, the URL will look like:
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
# SQLALCHEMY_DATABASE_URL = "mysql://user:password@localhost/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL) 
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}) 

# Create a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
