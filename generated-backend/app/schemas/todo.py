"""Pydantic schemas for Todo."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class TodoBase(BaseModel):
    """Base Todo schema."""


class TodoCreate(TodoBase):
    """Schema for creating Todo."""

    pass


class TodoUpdate(BaseModel):
    """Schema for updating Todo."""


class TodoResponse(TodoBase):
    """Schema for Todo response."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
