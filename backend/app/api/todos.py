FastAPI provides a simple way to define APIs and also integrates well with SQL databases using SQLAlchemy ORM. Here is a sample code to setup a database for storing todos and creating API endpoints to interact with it.

```python
# Necessary imports
from typing import List
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic models
class TodoBase(BaseModel):
    title: str
    description: str
    completed: bool

class Todo(TodoBase):
    id: int

    class Config:
        orm_mode = True

# SQLAlchemy models
class TodoModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# Application setup
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/todos/", response_model=Todo, status_code=201)
def create_todo(todo: TodoBase, db: Session = Depends(get_db)):
    """
    Create a new todo
    """
    db_todo = TodoModel(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos/", response_model=List[Todo])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Read todos with pagination
    """
    todos = db.query(TodoModel).offset(skip).limit(limit).all()
    return todos

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: TodoBase, db: Session = Depends(get_db)):
    """
    Update a todo
    """
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in todo.dict().items():
        setattr(db_todo, key, value)
    db.commit()
    return db_todo
```

In this code, we first setup SQLAlchemy to use SQLite database and define our todo model. We use Pydantic to define request/response models and validate the data. Then, we define FastAPI application and create endpoints to create, read and update todos. We use dependency injection to manage database sessions.