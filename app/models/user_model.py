from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import date


# ---------- Payment and Segmentation ----------
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


# ---------- Auth: Signup, Login ----------
class UserRegister(BaseModel):
    email: EmailStr
    password: str  # Required for normal signup
    name: str
    payment: Optional[PaymentInfo] = None
    segmentation_data: Optional[List[SegmentationData]] = []

class UserLogin(BaseModel):
    email: EmailStr
    password: str  # Required for email login


# ---------- Auth: OAuth Login ----------
class OAuthLogin(BaseModel):
    provider: str  # "google", "github", "linkedin"
    oauth_token: str  # ID token or access token/code (required)
    # Backend will decode email/name from this token
    # Optional if you're manually passing them
    email: Optional[EmailStr] = None
    name: Optional[str] = None


# ---------- Auth: Response ----------
class LoginResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
