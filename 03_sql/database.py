from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Index


DATABASE_URL = "postgresql+psycopg2://stud:stud@db:5432/archdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    age = Column(Integer, nullable=True)

Index('idx_user_name', User.first_name, User.last_name)

class Goal(Base):
    __tablename__ = "goals"
    id = Column(String, primary_key=True, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="goals")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(String, primary_key=True, index=True)
    description = Column(String)
    status = Column(String, default="pending")
    goal_id = Column(String, ForeignKey("goals.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))

    goal = relationship("Goal", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")

User.goals = relationship("Goal", order_by=Goal.id, back_populates="owner")
Goal.tasks = relationship("Task", order_by=Task.id, back_populates="goal")
User.assigned_tasks = relationship("Task", order_by=Task.id, back_populates="assignee")

Base.metadata.create_all(bind=engine)