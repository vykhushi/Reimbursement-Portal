import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
import models
from models import Base, User, Dept,FormData
import os
import uuid
from datetime import date
from io import BytesIO

# Create a new database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the testing database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Set up the TestClient
client = TestClient(app)

class TestAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create the database tables
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        # Drop the database tables
        Base.metadata.drop_all(bind=engine)

    def setUp(self):
        self.db = TestingSessionLocal()
        self.create_admin_user()  # Create an admin user in the setup
        self.create_employee_user() 

    def tearDown(self):
        self.db.close()


#USER TEST CASES

    def create_admin_user(self):
        admin_user = self.db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password="adminpassword",
                role="admin",
                department="admin_department",
                is_admin=True,
                manager_id=None  
            )
            print("Admin Created")
            self.db.add(admin_user)
            self.db.commit()
            

    def test_create_user(self):
        user_data = {
            "username": "testuser" + os.urandom(4).hex(),
            "email": "testuser" + os.urandom(4).hex() + "@example.com",
            "password": "testpassword",
            "role": "employee",
            "department": "test_department",
            "is_admin": False,
            "manager_id": None
        }

        response = client.post("/users/", json=user_data)
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertEqual(response_json["username"], user_data["username"])
        self.assertEqual(response_json["email"], user_data["email"])
        self.assertEqual(response_json["role"], user_data["role"])
        self.assertEqual(response_json["department"], user_data["department"])
        # self.assertIn("id", response_json)
        print("User Created")

    def test_create_user_missing_fields(self):
        user_data = {
            "username": "testuser" + os.urandom(4).hex(),
            # Missing email, password, role, department
            "is_admin": False,
            "manager_id": None
        }

        response = client.post("/users/", json=user_data)
        self.assertEqual(response.status_code, 422)  # Unprocessable Entity
        print("Test passed for invalid")

    #creating user with missin fields
    def test_create_user_missing_fields(self):
        user_data = {
            "username": "testuser" + os.urandom(4).hex(),
            # Missing email, password, role, department
            "is_admin": False,
            "manager_id": None
        }

        response = client.post("/users/", json=user_data)
        self.assertEqual(response.status_code, 422) 
        print("test passed for missing fields")
 
    #read user
    def test_read_users(self):
        response = client.get("/users/")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)
        print("test passes for read user")
    
    #create eployee user
    def create_employee_user(self):
        employee_user = self.db.query(User).filter(User.email == "employee@example.com").first()
        if not employee_user:
            employee_user = User(
                username="employee",
                email="employee@example.com",
                password="employeepassword",
                role="employee",
                department="employee_department",
                is_admin=False,
                manager_id=None
            )
            self.db.add(employee_user)
            self.db.commit()
            print("test passes for employee user")

   #Delete user by email
    def test_delete_user_by_email(self):
        # First create a user to delete
        user_data = {
            "username": "deleteuser" + os.urandom(4).hex(),
            "email": "deleteuser" + os.urandom(4).hex() + "@example.com",
            "password": "deletepassword",
            "role": "employee",
            "department": "delete_department",
            "is_admin": False,
            "manager_id": None
        }
        response = client.post("/users/", json=user_data)
        self.assertEqual(response.status_code, 201)
        user_email = user_data["email"]

        # Delete the user by email
        response = client.delete(f"/users/{user_email}")
        self.assertEqual(response.status_code, 204)


    #Delete user with non existence email
    def test_delete_non_existent_user_by_email(self):
        non_existent_email = "nonexistentuser@example.com"
        response = client.delete(f"/users/{non_existent_email}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "User not found")

    



  #DEPARTMENT TEST CASES
    #create department 
    def test_create_department(self):
        dept_name = "ABC" + os.urandom(4).hex()
        response = client.post("/departments/", json={"dept_name": dept_name})
        self.assertEqual(response.status_code, 200)
        self.assertIn("ABC", response.text)
        print("test passes for creating departments")


    #read department 
    def test_read_departments(self):
        dept_name = "ABC" + os.urandom(4).hex()  # Create a unique department name
        response = client.post("/departments/", json={"dept_name": dept_name})
        self.assertEqual(response.status_code, 200)
        response = client.get("/departments/")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()), 0)
        print("test passes for read department")

    

    #delete the department
    def create_department(self, dept_name):
        department = Dept(dept_name=dept_name)
        self.db.add(department)
        self.db.commit()
        self.db.refresh(department)
        return department

    def test_delete_department(self):
        # Create a department to be deleted
        department = self.create_department("Test Department")

        # Delete the department
        response = client.delete(f"/departments/{department.id}")
        self.assertEqual(response.status_code, 204)

        # Verify the department is deleted
        response = client.get("/departments/")
        departments = response.json()
        self.assertNotIn(department.id, [dept['id'] for dept in departments])

    def test_delete_nonexistent_department(self):
        # Try to delete a department that does not exist
        response = client.delete("/departments/999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Department not found"})
   

    def test_submit_form(self):
        form_data = {
            "Name": (None, "Test Form"),
            "Expense_Type": (None, "Travel"),
            "Amount": (None, "100"),
            "Date": (None, str(date(2024, 1, 1))),
            "file": ("test.jpg", BytesIO(b"file content"), "image/jpeg"),
            "Comment": (None, "Test comment"),
            "Status": (None, "Pending"),
            "Employee_id": (None, "1")
        }

        response = client.post("/forms/", files=form_data)
        print("Response status code:", response.status_code)
        print("Response JSON:", response.json())
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json["Name"], "Test Form")
        self.assertEqual(response_json["Expense_Type"], "Travel")
        self.assertEqual(response_json["Amount"], 100)
        self.assertEqual(response_json["Date"], "2024-01-01")
        self.assertEqual(response_json["Comment"], "Test comment")
        self.assertEqual(response_json["Status"], "Pending")
        self.assertIn("Image_Url", response_json)




        # Helper method to create form data
    def create_form_data(self):
        form_data = FormData(
            Employee_id=1,
            Name="Test Form",
            Expense_Type="Travel",
            Amount=100,
            Date=date(2024, 1, 1),
            Image_Url="/claimImages/test.jpg",
            Comment="Test comment",
            Status="Pending"
        )
        self.db.add(form_data)
        self.db.commit()
        self.db.refresh(form_data)
        return form_data

     # Test case for getting form data
    def test_get_form_data(self):
        # First, create some form data
        self.create_form_data()

        # Call the endpoint to get the form data
        response = client.get("/table/")
        self.assertEqual(response.status_code, 200)

        # Verify the response data
        response_json = response.json()
        
        self.assertGreater(len(response_json), 0)
        form_data = response_json[0]
        self.assertEqual(form_data["Name"], "Test Form")
        self.assertEqual(form_data["Expense_Type"], "Travel")
        self.assertEqual(form_data["Amount"], 100)
        self.assertEqual(form_data["Date"], "2024-01-01")
        self.assertEqual(form_data["Comment"], "Test comment")
        self.assertEqual(form_data["Status"], "Pending")


    # Helper method to create claim requests
def create_claim_requests(self):
    # Create some claim requests for the user with id=1
    user_id = 1
    for i in range(3):
        claim = FormData(
            Employee_id=user_id,
            Name=f"Test Claim {i+1}",
            Expense_Type="Travel",
            Amount=100,
            Date="2024-01-01",
            Image_Url="/claimImages/test.jpg",
            Comment="Test comment",
            Status="Pending"
        )
        self.db.add(claim)
    self.db.commit()

    # Test case for getting claim requests of a particular employee
    def test_get_claim_requests(self):
        response = client.get("/get_claim_request/1")
        self.assertEqual(response.status_code, 200)

        claims = response.json()
        print("Response JSON for getting claims:", response.json())
        self.assertEqual(len(claims), 3)  # Check if 3 claims were returned for user with id=1




def test_update_form(self):
    # First, create a form data to be updated
    form_data = self.create_form_data()
    form_id = form_data.id  # Get the ID of the created form

    # Next, update the form data
    update_data = {
        "Name": "Updated Form Name",
        "Amount": 200,
        "Status": "Approved"
    }
    response = client.put(f"/expense/{form_id}", json=update_data)
    self.assertEqual(response.status_code, 200)
    updated_form = response.json()
    self.assertEqual(updated_form["Name"], "Updated Form Name")
    self.assertEqual(updated_form["Amount"], 200)
    self.assertEqual(updated_form["Status"], "Approved")

    # Verify that other fields remain unchanged
    self.assertEqual(updated_form["Expense_Type"], "Travel")
    self.assertEqual(updated_form["Date"], str(date(2024, 1, 1)))
    self.assertEqual(updated_form["Image_Url"], "/claimImages/test.jpg")
    self.assertEqual(updated_form["Comment"], "Test comment")


def test_update_form_not_found(self):
    # Test updating a non-existent form
    form_id = 999
    update_data = {
        "Name": "Updated Form Name",
        "Amount": 200,
        "Status": "Approved"
    }
    response = client.put(f"/expense/{form_id}", json=update_data)
    self.assertEqual(response.status_code, 404)
    self.assertEqual(response.json(), {"detail": "Form not found"})

if __name__ == "__main__":
    unittest.main()


