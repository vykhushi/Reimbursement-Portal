import sys
import os
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the current directory to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app, get_db
from models import Base, User, FormData, Dept

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency with the test database session
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Create all the tables in the test database
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def test_client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/", json={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "password123",
            "role": "employee",
            "department": "IT",
            "is_admin": False,
            "manager_id": None
        })
    assert response.status_code == 201
    assert response.json()["email"] == "testuser@example.com"

# @pytest.mark.asyncio
# async def test_delete_user():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/users/", json={
#             "username": "testdeleteuser",
#             "email": "testdeleteuser@example.com",
#             "password": "password123",
#             "role": "employee",
#             "department": "IT",
#             "is_admin": False,
#             "manager_id": None
#         })
#         response = await ac.delete("/users/testdeleteuser@example.com")
#     assert response.status_code == 204

# @pytest.mark.asyncio
# async def test_authenticate_user():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/users/", json={
#             "username": "testauthuser",
#             "email": "testauthuser@example.com",
#             "password": "password123",
#             "role": "employee",
#             "department": "IT",
#             "is_admin": False,
#             "manager_id": None
#         })
#         response = await ac.post("/login/", json={
#             "email": "testauthuser@example.com",
#             "password": "password123"
#         })
#     assert response.status_code == 200
#     assert response.json()["message"] == "Login successful"



