from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=40)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)

class LoginIn(BaseModel):
    username: str
    password: str

class HomeIn(BaseModel):
    budget: float = Field(gt=0)
    lights: int = 0
    fans: int = 0
    furniture: int = 0
    dining_tables: int = 0
    rooms: List[str] = []
    notes: Optional[str] = ""

class PartyIn(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0)
    event_type: str = "Birthday"
    venue: str = "Home"
    needs: List[str] = []
    notes: Optional[str] = ""

class JewelryIn(BaseModel):
    budget: float = Field(gt=0)
    occasion: str = "Birthday"
    style: str = "Elegant"
    notes: Optional[str] = ""
