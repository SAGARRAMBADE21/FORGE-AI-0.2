"""Pydantic schemas for useField."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class useFieldBase(BaseModel):
    """Base useField schema."""



class useFieldCreate(useFieldBase):
    """Schema for creating useField."""
    pass


class useFieldUpdate(BaseModel):
    """Schema for updating useField."""



class useFieldResponse(useFieldBase):
    """Schema for useField response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True