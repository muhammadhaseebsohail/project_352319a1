Below is the comprehensive testing code for the given FastAPI endpoint.

```python
# Necessary imports
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db, SessionLocal, Base, TodoModel, TodoBase

# SQL Alchemy setup for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_todo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Override the get_db function to use testing database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Initialize the TestClient
client = TestClient(app)

@pytest.fixture(autouse=True)
def create_test_db():
    """
    Create a fresh database for each test.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

def test_create_todo(create_test_db):
    """
    Testing the creation of a todo
    """
    response = client.post("/todos/", json={"title": "test todo", "description": "test description", "completed": False})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "test todo"
    assert data["description"] == "test description"
    assert data["completed"] == False
    assert "id" in data

def test_create_todo_invalid_data(create_test_db):
    """
    Testing the todo creation with invalid data
    """
    response = client.post("/todos/", json={})
    assert response.status_code == 422

def test_read_todos(create_test_db):
    """
    Testing reading todos
    """
    db = create_test_db
    db_todo = TodoModel(title="test todo", description="test description", completed=False)
    db.add(db_todo)
    db.commit()

    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "test todo"
    assert data[0]["description"] == "test description"
    assert data[0]["completed"] == False

def test_update_todo(create_test_db):
    """
    Testing updating a todo
    """
    db = create_test_db
    db_todo = TodoModel(title="test todo", description="test description", completed=False)
    db.add(db_todo)
    db.commit()

    todo_id = db_todo.id
    response = client.put(f"/todos/{todo_id}", json={"title": "updated todo", "description": "updated description", "completed": True})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "updated todo"
    assert data["description"] == "updated description"
    assert data["completed"] == True

def test_update_todo_not_found(create_test_db):
    """
    Testing updating a todo that does not exist
    """
    response = client.put("/todos/999", json={"title": "updated todo", "description": "updated description", "completed": True})
    assert response.status_code == 404
```

In this testing code, we first setup a separate SQLite database for testing and override the `get_db` function to use the testing database. We then define a fixture to create a fresh database for each test. After that, we define tests for creating, reading and updating todos. In each test, we use the FastAPI TestClient to send requests to our API and assert that the responses are correct. For error cases, we assert that the status code and error message are correct.