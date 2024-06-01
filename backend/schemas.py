from pydantic import BaseModel
from typing import Optional
from datetime import date
from fastapi import UploadFile

class CreateUser(BaseModel):
    username: str
    email: str
    password: str
    role: str
    department: str
    is_admin:bool
    manager_id:Optional[int] = None 

class UserAuthenticate(BaseModel):
    email: str
    password: str


class GetFormData(BaseModel):
    Name:str
    Employee_id:int
    Expense_Type: str
    Amount: int
    Date:date
    Image_Url:str
    Comment:str
    Status:str
    
    
    class Config:
        orm_mode = True 



class AddDepartment(BaseModel):
    dept_name:str

   











