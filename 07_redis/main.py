from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, User, Goal, redis_client
from mongo import tasks_collection
import uuid
from bson import ObjectId
import json
from sqlalchemy.exc import IntegrityError

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    age: Optional[int] = None

class GoalCreate(BaseModel):
    description: str

class GoalResponse(BaseModel):
    id: str
    description: str
    owner_id: int

class TaskCreate(BaseModel):
    description: str
    assignee_id: int

class TaskResponse(BaseModel):
    id: str
    description: str
    status: str
    goal_id: str
    assignee_id: int

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_client(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        return user
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
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == form_data.username).first()
        if user and pwd_context.verify(form_data.password, user.hashed_password):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users", response_model=List[UserResponse])
def get_users(current_user: User = Depends(get_current_client), db: Session = Depends(get_db)):
    try:
        return db.query(User).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, current_user: User = Depends(get_current_client), db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(
            (User.username == user.username) | (User.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )

        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            first_name=user.first_name,
            last_name=user.last_name,
            age=user.age
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users/search", response_model=List[UserResponse])
def search_users(query: str, current_user: User = Depends(get_current_client), db: Session = Depends(get_db)):
    try:
        users = db.query(User).filter(
            (User.first_name.ilike(f"%{query}%")) | (User.last_name.ilike(f"%{query}%"))
        ).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_user_from_cache(user_id: int):
    try:
        user_data = redis_client.get(f"user:{user_id}")
        if user_data:
            return json.loads(user_data)
        return None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def set_user_to_cache(user: User):
    try:
        redis_client.set(f"user:{user.id}", json.dumps({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age
        }), ex=3600)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: User = Depends(get_current_client), db: Session = Depends(get_db)):
    try:
        cached_user = get_user_from_cache(user_id)
        if cached_user:
            return cached_user

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        set_user_to_cache(user)

        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/goals", response_model=GoalResponse)
def create_goal(goal: GoalCreate, current_user: User = Depends(get_current_client), db: Session = Depends(get_db)):
    try:
        db_goal = Goal(
            id=str(uuid.uuid4()),
            description=goal.description,
            owner_id=current_user.id
        )
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        return db_goal
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/goals", response_model=List[GoalResponse])
def get_goals(current_user: User = Depends(get_current_client), db: Session = Depends(get_db)):
    try:
        return db.query(Goal).filter(Goal.owner_id == current_user.id).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/goals/{goal_id}/tasks", response_model=TaskResponse)
def create_task(
    goal_id: str, 
    task: TaskCreate,
    current_user: User = Depends(get_current_client),
    db: Session = Depends(get_db)
):
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")

        assignee = db.query(User).filter(User.id == task.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")

        task_data = {
            "description": task.description,
            "goal_id": goal_id,
            "assignee_id": task.assignee_id,
            "status": "pending"
        }
        result = tasks_collection.insert_one(task_data)
        task_id = str(result.inserted_id)

        return {
            "id": task_id,
            **task_data
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/goals/{goal_id}/tasks", response_model=List[TaskResponse])
def get_tasks(goal_id: str, current_user: User = Depends(get_current_client)):
    try:
        tasks = list(tasks_collection.find({"goal_id": goal_id}))
        return [{"id": str(task["_id"]), **task} for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task_status(task_id: str, status: str, current_user: User = Depends(get_current_client)):
    try:
        task_object_id = ObjectId(task_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    try:
        task = tasks_collection.find_one({"_id": task_object_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        tasks_collection.update_one({"_id": task_object_id}, {"$set": {"status": status}})
        
        updated_task = tasks_collection.find_one({"_id": task_object_id})
        
        return {"id": str(updated_task["_id"]), **updated_task}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)