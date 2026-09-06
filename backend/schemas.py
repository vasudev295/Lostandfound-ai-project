from pydantic import BaseModel, Field
from typing import Optional

class RegisterIn(BaseModel):
    name:str
    email:str
    password:str=Field(min_length=6)

class LoginIn(BaseModel):
    email:str
    password:str

class ItemIn(BaseModel):
    item_type:str=Field(pattern="^(lost|found)$")
    title:str
    description:str
    location:str
    category:str="Other"
    contact:Optional[str]=None

class ClaimIn(BaseModel):
    message:str

class StatusIn(BaseModel):
    status:str=Field(pattern="^(active|resolved)$")
