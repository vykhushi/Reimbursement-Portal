from sqlalchemy import Column, Integer, String,Float,Date,LargeBinary,ForeignKey,Boolean
from sqlalchemy.ext.declarative import declarative_base
from fastapi import UploadFile
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    department = Column(String(50), nullable=False)
    is_admin = Column(Boolean, default=False)
    manager_id = Column(Integer, ForeignKey('users.id'))


    

    #Relationship to access employees managed by the user
    employees = relationship("User", back_populates="manager")

    #  # Relationship to access the manager of the user
    manager = relationship("User", back_populates="employees", remote_side=[id])#(m-1)

   


   

class FormData(Base):
    __tablename__='forms' 

    id = Column(Integer, primary_key=True, index=True)
    Name=Column(String(50), unique=False, nullable=False)
    Expense_Type=Column(String(50), unique=False, nullable=False)
    Amount=Column(Integer, unique=False, nullable=False)
    Date=Column(Date)
    Image_Url =  Column(String(1000)) 






   
    



    


