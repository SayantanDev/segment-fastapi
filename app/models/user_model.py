from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import date

class PaymentPlan(BaseModel):
    payment_plan: str
    payment_amount: float
    start_date: date
    end_date: date

class PaymentInfo(BaseModel):
    payment_status: bool
    plans: List[PaymentPlan]

class ConfigItem(BaseModel):
    config_name: str
    config_model: Dict[str, Any]

class SegmentationData(BaseModel):
    session_id: str
    config_data: List[ConfigItem]

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    payment: Optional[PaymentInfo] = None
    segmentation_data: Optional[List[SegmentationData]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class OAuthLogin(BaseModel):
    email: EmailStr
    name: Optional[str]
    provider: str  # e.g., google, github, linkedin
    oauth_token: Optional[str] = None

class LoginResponse(BaseModel):
    id: str
    email: EmailStr
    name: str