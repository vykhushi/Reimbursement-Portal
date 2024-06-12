from ast import Name
from fastapi import FastAPI, HTTPException, Query, status, Depends,UploadFile,File,Form,APIRouter,Request
from pathlib import Path
from typing import List
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
from schemas import CreateUser,UserAuthenticate,GetFormData,AddDepartment
import models 
import schemas
from models import  User as DBUser
from models import Dept
from models import FormData
from typing import Optional
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



logging.basicConfig(
       filename='app.log', 
       level=(logging.DEBUG),  
       format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)

# API endpoint to create a new user

@app.post("/users/", response_model=CreateUser, status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    try:      
        admin_user = db.query(DBUser).filter(DBUser.role == 'admin').first()
        if not admin_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
        # print("abc")
        db_user = DBUser(
              
              username=user.username,
              email=user.email,
              password=user.password,
              role=user.role,
              department=user.department,
              manager_id=admin_user.id  
              
            )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user 
    
    except Exception as e:
      logging.error(f"Failed to create user: {e}")
      print(e)
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

#API endpoint to delete user using email
@app.delete("/users/{user_email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_email: str, db: Session = Depends(get_db)):
    logging.info(f"Deleting user with email: {user_email}")
    user = db.query(DBUser).filter(DBUser.email== user_email).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}


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



#API endpoint to assign manager to employees
@app.put("/assign_manager/{manager_email}/employees/{employee_email}", response_model=CreateUser)
def assign_manager_to_employee(manager_email: str, employee_email: str, db: Session = Depends(get_db)):
    try:
      
        logging.info(f"Looking for manager with email: {manager_email}")
        logging.info(f"Looking for employee with email: {employee_email}")

     
        manager = db.query(DBUser).filter(DBUser.email == manager_email).first()
        employee = db.query(DBUser).filter(DBUser.email == employee_email).first()
        

        if not employee or not manager:
            
            logging.error(f"Employee or manager not found: employee={employee}, manager={manager}")
            raise HTTPException(status_code=404, detail="Employee or manager not found")

        employee.manager_id = manager.id  # Assuming manager_id is stored in the manager's User object
        db.commit()
        db.refresh(employee)
        return employee

    except Exception as e:
        logging.error(f"Failed to assign manager to employee: {e}")
        raise


#API endpoint to find the suboordinates under a manager 
@app.get("/manager/{manager_email}/employees/", response_model=None)
def get_employees_managed_by_manager(manager_email: str, db: Session = Depends(get_db)):
    try:
        manager = db.query(DBUser).filter(DBUser.email == manager_email).first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")
           

        employees = db.query(DBUser).filter(DBUser.manager_id == manager.id).all()
        if not employees:
            #raise HTTPException(status_code=404, detail="No employees found for this manager")
            return []
        
        return employees
    
    except Exception as e:
        logging.error(f"Failed to retrieve employees managed by manager: {e}")
        raise

#API endpoint to find employees
@app.get("/employees/", response_model=None)
def read_employee_users(db: Session = Depends(get_db)):
    logging.info("Fetching all employees")
    employees = db.query(DBUser).filter(DBUser.role == 'employee').all()
    return employees



#API endpoint to find managers
@app.get("/managers/", response_model=None)
def read_manager_users(db: Session = Depends(get_db)):
    logging.info("Fetching all managers")
    managers = db.query(DBUser).filter(DBUser.role == 'manager').all()
    return managers


#API endpoint to submit the claim form
@app.post("/forms/", response_model=GetFormData)
async def submit_form(
    request:Request,
    Name:str = Form(...),
    Expense_Type: str = Form(...),
    Amount: int = Form(...),
    Date: date = Form(...),
    file: UploadFile = File(...),
    Comment:str=Form(...),
    Status:str=Form(...),
    Employee_id:int=Form(...)
):
   logging.info("Submitting a new claim form")
   form_data = await request.form()

    # Convert the form data to a dictionary for easy inspection
   form_data_dict = dict(form_data)
   print(form_data_dict)
   
   
   try:
        # Validate and parse form data using Pydantic schema
        form_data = GetFormData(Name=Name ,Expense_Type=Expense_Type, Amount=Amount, Date=Date, Image_Url="",Comment=Comment,Status=Status,Employee_id=Employee_id)

        
         # Save the uploaded image file to the "receipt_images" folder
        contents = await file.read()
        image_filename = f"{uuid.uuid4()}.jpg"
        current_folder = os.getcwd()
        parent_folder = os.path.dirname(current_folder)
        target_folder = os.path.join(parent_folder, "claimImages")
        os.makedirs(target_folder, exist_ok=True)
        image_path = os.path.join(target_folder, image_filename)
    
        with open(image_path, "wb") as image_file:
            image_file.write(contents)

        # Construct the Image_Url for the FormData object
        image_url = f"/claimImages/{image_filename}"

        # Create a FormData object to store in the database
        db_form_data = FormData(
            Name=form_data.Name,
            Expense_Type=form_data.Expense_Type,
            Amount=form_data.Amount,
            Date=form_data.Date,
            Image_Url= image_url,
            Comment=Comment,
            Status=Status,
            Employee_id=form_data.Employee_id,  
        )

        # Save FormData object to the database using SQLAlchemy
        db = next(get_db())
        db.add(db_form_data)
        db.commit()
        db.refresh(db_form_data)

        return db_form_data
    
   except Exception as e:
            logging.error(f"Failed to submit form: {e}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
   

     
#API endpointto to get the data from the claim from in records table  
@app.get("/table/", response_model=None)
def get_data(db: Session = Depends(get_db)):
    logging.info("Fetching all form data")
    # Use the provided database session (`db`) to query FormDat

    form_data_list=db.query(FormData).all()
    for i in range(len(form_data_list)):
        print(form_data_list[i].id)
    return form_data_list


#API endpoint to get  claim request of a particular employee
@app.get("/get_claim_request/{id}", response_model=None)
def read_users(id:int,db: Session = Depends(get_db)):
    logging.info(f"Fetching claim requests for employee with id: {id}")
    claims = db.query(FormData).filter(FormData.Employee_id==id).all()
    return claims

       
#API endpoint to update the status of employee
@app.put("/expense/{form_id}")
async def update_form(
    form_id: int,
    Name: Optional[str] = Query(None),
    Expense_Type: Optional[str] = Query(None),
    Amount: Optional[int] = Query(None),
    Date: Optional[date] = Query(None),
    Image_Url: Optional[str] = Query(None),
    Comment: Optional[str] = Query(None),
    Status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):   
    logging.info(f"Updating form with id: {form_id}")
    form = db.query(FormData).filter(FormData.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    if Name is not None:
        form.Name = Name
    if Expense_Type is not None:
        form.Expense_Type = Expense_Type
    if Amount is not None:
        form.Amount = Amount
    if Date is not None:
        form.Date = Date
    if Image_Url is not None:
        form.Image_Url = Image_Url
    if Comment is not None:
        form.Comment = Comment
    if Status is not None:
        form.Status = Status

    db.commit()
    db.refresh(form)
    return form



#API endpoint to get all registered user
@app.get("/users/", response_model=None)
def read_users(db: Session = Depends(get_db)):
    logging.info("Fetching all users")
    users = db.query(DBUser).all()
    for i in range(len(users)):
        return users
    

#API endpoint to get user by email 
@app.get("/get_user/{email}", response_model=None)
def read_users(email:str,db: Session = Depends(get_db)):
    logging.info(f"Fetching user with email: {email}") 
    user = db.query(DBUser).filter(DBUser.email==email).first()
    return user


#API endpoint to create department(add dept)
@app.post("/departments/", response_model=AddDepartment)
def create_department(dept: AddDepartment, db: Session = Depends(get_db)):
    logging.info(f"Creating department with name: {dept.dept_name}")
    db_dept = Dept(dept_name=dept.dept_name)
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return dept


#API endpoint to get all the dept 
@app.get("/departments/", response_model=None)
def read_dept(db: Session = Depends(get_db)):
    logging.info("Fetching all departments")
    departments= db.query(Dept).all()
    return departments


#API endpoint to delete the dept 
@app.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id: int, db: Session = Depends(get_db)):
    logging.info(f"Deleting department with id: {department_id}")

    department = db.query(Dept).filter(Dept.id == department_id).first()
    
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    db.delete(department)
    db.commit()
    return {"detail": "Department deleted successfully"}



if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="127.0.0.1", port=8000)



