from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Секретный ключ для подписи JWT
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Модель данных для пользователя
class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    age: Optional[int] = None

# Временное хранилище для пользователей
users_db = []

# Псевдо-база данных пользователей
fake_users_db = {
    "johndoe": {
        "id": 1,
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # hashed "secret"
        "age": 30,
    }
}

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Создание и проверка JWT токенов
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Получение пользователя из псевдо-базы данных
def get_user_from_db(fake_db, username: str):
    if username in fake_db:
        user_dict = fake_db[username]
        return User(**user_dict)

# Аутентификация пользователя
def authenticate_user(fake_db, username: str, password: str):
    user = get_user_from_db(fake_db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

# Зависимости для получения текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        print('jwt error')
        raise credentials_exception
    user = get_user_from_db(fake_users_db, username=username)
    if user is None:
        raise credentials_exception
    return user

# Маршрут для получения токена
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# GET /users - Получить всех пользователей (требует аутентификации)
@app.get("/users", response_model=List[User])
def get_users(current_user: User = Depends(get_current_user)):
    return users_db

# GET /users/{user_id} - Получить пользователя по ID (требует аутентификации)
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# POST /users - Создать нового пользователя (требует аутентификации)
@app.post("/users", response_model=User)
def create_user(user: User, current_user: User = Depends(get_current_user)):
    users_db.append(user)
    return user

# PUT /users/{user_id} - Обновить пользователя по ID (требует аутентификации)
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, current_user: User = Depends(get_current_user)):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            users_db[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

# DELETE /users/{user_id} - Удалить пользователя по ID (требует аутентификации)
@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            deleted_user = users_db.pop(index)
            return deleted_user
    raise HTTPException(status_code=404, detail="User not found")

# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации


# Примеры запросов:
# POST /token: Получить токен для аутентификации.
# json
# {
#   "username": "johndoe",
#   "password": "secret"
# }
# GET /users: Получить всех пользователей (требует токен).

# GET /users/{user_id}: Получить пользователя по ID (требует токен).
# POST /users: Создать нового пользователя (требует токен).
# PUT /users/{user_id}: Обновить пользователя по ID (требует токен).
# {
#   "id": 2,
#   "username": "janedoe",
#   "email": "janedoe@example.com",
#   "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # hashed "secret"
#   "age": 26
# }
# DELETE /users/{user_id}: Удалить пользователя по ID (требует токен).

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)