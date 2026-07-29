from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# --- Authentication Schemas ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# --- Analysis Schemas ---

class AnalysisRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None

    @validator('text')
    def validate_inputs(cls, v, values):
        url = values.get('url')
        if not url and not v:
            raise ValueError('Either URL or raw text must be provided')
        return v


class AnalysisResponse(BaseModel):
    id: int
    user_id: int
    title: str
    url: Optional[str]
    summary: str
    
    original_left: float
    original_center: float
    original_right: float
    
    debiased_text: str
    
    debiased_left: float
    debiased_center: float
    debiased_right: float
    
    bias_reduction: float
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
