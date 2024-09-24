from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import os

# Настройка SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db/postgres")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель SQLAlchemy
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Модель Pydantic для валидации данных
class UserCreate(BaseModel):
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

app = FastAPI()

# Зависимости для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршрут для создания пользователя
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), tags=["Users"]):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Маршрут для получения пользователя по id
@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Маршрут для получения всех пользователей
@app.get("/users/", response_model=list[UserResponse], tags=["Users"])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)