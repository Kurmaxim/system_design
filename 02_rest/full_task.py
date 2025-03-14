from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    first_name: str  
    last_name: str   
    age: Optional[int] = None

class Goal(BaseModel):
    id: str
    description: str
    owner_id: int 

class Task(BaseModel):
    id: str
    description: str
    status: str = "pending" 
    goal_id: str  
    assignee_id: int 

users_db = []
goals_db = {}
tasks_db = {}

client_db = {
    "admin": {
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # hashed "secret"
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@example.com",
        "age": 30
    }
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_client(token: str = Depends(oauth2_scheme)):
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
        else:
            return username
    except JWTError:
        raise credentials_exception

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        password_check = False
        if form_data.username in client_db:
            user_data = client_db[form_data.username]
            if pwd_context.verify(form_data.password, user_data["hashed_password"]):
                password_check = True

        if password_check:
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users", response_model=List[User])
def get_users(current_user: str = Depends(get_current_client)):
    try:
        return users_db
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/users", response_model=User)
def create_user(user: User, current_user: str = Depends(get_current_client)):
    try:
        for u in users_db:
            if u.id == user.id:
                raise HTTPException(status_code=400, detail="User already exists")
        users_db.append(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users/search", response_model=List[User])
def search_users(query: str, current_user: str = Depends(get_current_client)):
    try:
        result = []
        for user in users_db:
            if query.lower() in user.first_name.lower() or query.lower() in user.last_name.lower():
                result.append(user)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, current_user: str = Depends(get_current_client)):
    try:
        for user in users_db:
            if user.id == user_id:
                return user
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/goals", response_model=Goal)
def create_goal(goal: Goal, current_user: str = Depends(get_current_client)):
    try:
        if goal.id in goals_db:
            raise HTTPException(status_code=400, detail="Goal already exists")
        goals_db[goal.id] = goal
        return goal
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/goals", response_model=List[Goal])
def get_goals(current_user: str = Depends(get_current_client)):
    try:
        return list(goals_db.values())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/goals/{goal_id}/tasks", response_model=Task)
def create_task(goal_id: str, task: Task, current_user: str = Depends(get_current_client)):
    try:
        if goal_id not in goals_db:
            raise HTTPException(status_code=404, detail="Goal not found")
        if task.id in tasks_db:
            raise HTTPException(status_code=400, detail="Task already exists")
        tasks_db[task.id] = task
        return task
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/goals/{goal_id}/tasks", response_model=List[Task])
def get_tasks(goal_id: str, current_user: str = Depends(get_current_client)):
    try:
        if goal_id not in goals_db:
            raise HTTPException(status_code=404, detail="Goal not found")
        return [task for task in tasks_db.values() if task.goal_id == goal_id]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.put("/tasks/{task_id}", response_model=Task)
def update_task_status(task_id: str, status: str, current_user: str = Depends(get_current_client)):
    try:
        if task_id not in tasks_db:
            raise HTTPException(status_code=404, detail="Task not found")
        tasks_db[task_id].status = status
        return tasks_db[task_id]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)