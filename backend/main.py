from ast import Name
from fastapi import FastAPI, HTTPException, status, Depends,UploadFile,File,Form,APIRouter
from pathlib import Path
from typing import List
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
from schemas import CreateUser,UserAuthenticate,GetFormData
import models 
import schemas
from models import  User as DBUser

from models import FormData

from database import SessionLocal,engine
from sqlalchemy.orm import Session
import os
import uuid
import logging


app = FastAPI()
router = APIRouter()
models.Base.metadata.create_all(bind=engine)

# Configure CORS settings
origins = [
    "http://localhost",         # Allow requests from this origin
    "http://localhost:8080",
    "http://127.0.0.1:5500"
        # Additional allowed origin (if applicable)
    # Add other origins as needed
]

# Add CORS middleware to allow requests from specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use "*" to allow requests from any origin 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API endpoint to create a new user

logging.basicConfig(
       filename='app.log',  # Log file name
       level=(logging.DEBUG),  # Log level (e.g., DEBUG, INFO, ERROR)
       format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

@app.post("/users/", response_model=None, status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    try:
          db_user = DBUser(
              username=user.username,
              email=user.email,
              password=user.password,
              role=user.role,
              department=user.department
            )
          db.add(db_user)
          db.commit()
          db.refresh(db_user)
          return db_user
    
    except Exception as e:
      logging.error(f"Failed to create user: {e}")
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")





    
# API endpoint to authenticate a user
@app.post("/login/")
def authenticate_user(user_data:UserAuthenticate, db: Session = Depends(get_db)):
    try:
        user = db.query(DBUser).filter(DBUser.email == user_data.email).first()
        if not user or user.password != user_data.password:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
        return {"message": "Login successful"}
    except Exception as e:
        logging.error(f"Failed to authenticate user: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to authenticate user")




def designate_user_as_admin(email: str, db: Session):
    try:

        current_admin = db.query(DBUser).filter(DBUser.is_admin == True).first()
        if current_admin:
            current_admin.is_admin = False

        # Find the user by email

        user = db.query(DBUser).filter(DBUser.email == email).first()
    
        if user:
            user.is_admin = True
            db.commit()
            return f"User with email '{email}' is now an admin."
        else:
            logging.error(f"User with email '{email}' not found.")
            return f"User with email '{email}' not found."
    except Exception as e:
        logging.error(f"Failed to designate user as admin: {e}")
        return f"Failed to designate user as admin: {e}"


@app.put("/users/{email}/make_admin", response_model=str)
def make_user_admin(email: str, db: Session = Depends(get_db)):
    message = designate_user_as_admin(email, db)
    return message



@app.put("/employees/{employee_email}/assign_manager/{manager_email}", response_model=CreateUser)
def assign_manager_to_employee(employee_email: str, manager_email: str, db: Session = Depends(get_db)):
    try:
        employee = db.query(DBUser).filter(DBUser.email == employee_email).first()
        manager = db.query(DBUser).filter(DBUser.email == manager_email).first()

        if not employee or not manager:
            raise HTTPException(status_code=404, detail="Employee or manager not found")

        employee.manager_id = manager.id  # Assuming manager_id is stored in the manager's User object
        db.commit()
        db.refresh(employee)
        return employee

    except Exception as e:
        logging.error(f"Failed to assign manager to employee: {e}")
        raise

@app.get("/manager/{manager_email}/employees/", response_model=List[CreateUser])
def get_employees_managed_by_manager(manager_email: str, db: Session = Depends(get_db)):
    try:
        manager = db.query(DBUser).filter(DBUser.email == manager_email).first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")

        employees = db.query(DBUser).filter(DBUser.manager_id == manager.id).all()
        if not employees:
            raise HTTPException(status_code=404, detail="No employees found for this manager")
        
        return employees
    
    except Exception as e:
        logging.error(f"Failed to retrieve employees managed by manager: {e}")
        raise

#API endpoint to submit the claim form 

@app.post("/forms/", response_model=GetFormData)
async def submit_form(
    Name:str = Form(...),
    Expense_Type: str = Form(...),
    Amount: int = Form(...),
    Date: date = Form(...),
    file: UploadFile = File(...)
):
 
   try:
        # Validate and parse form data using Pydantic schema
        form_data = GetFormData(Name=Name ,Expense_Type=Expense_Type, Amount=Amount, Date=Date, Image_Url="")

        
         # Save the uploaded image file to the "receipt_images" folder
        contents = await file.read()
        image_filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join("receiptimage", image_filename)

        with open(image_path, "wb") as image_file:
            image_file.write(contents)

        # Construct the Image_Url for the FormData object
        image_url = f"/receiptimage/{image_filename}"

        # Create a FormData object to store in the database
        db_form_data = FormData(
            Name=form_data.Name,
            Expense_Type=form_data.Expense_Type,
            Amount=form_data.Amount,
            Date=form_data.Date,
            Image_Url= image_url
        )

        # Save FormData object to the database using SQLAlchemy
        db = next(get_db())
        db.add(db_form_data)
        db.commit()
        db.refresh(db_form_data)

        return db_form_data
    
   except Exception as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
   

@app.get("/table/", response_model=List[GetFormData])
async def get_data(db: Session = Depends(get_db)):
    # Use the provided database session (`db`) to query FormData
    form_data_list = db.query(FormData).all()
    return form_data_list

@app.get("/users/", response_model=List[CreateUser])
def read_users(db: Session = Depends(get_db)):
    users = db.query(DBUser).all()
    return users








if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="127.0.0.1", port=8000)



