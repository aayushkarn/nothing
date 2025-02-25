import re
from pydantic import BaseModel, EmailStr, field_validator, root_validator, validator
from typing import Optional

class UserRegistration(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password:str
    business_name:str
    business_ein:str

    # @field_validator('email')
    # def validate_email(cls,v):
    #     if v:
    #         EmailStr._validate(v)
    #     return v

    # @field_validator("phone")
    # def validate_phone(cls,v):
    #     if v:
    #         if not re.match(r'^\d{10}$', v):
    #             raise ValueError('Invalid phone number format')
    #     return v

    # @field_validator('password')
    # def validate_password(cls, v):
    #     if len(v) < 8:
    #         raise ValueError('Password must be at least 8 characters long')
    #     return v
    

class UserLogin(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    password:str

class UserVerification(BaseModel):
    email:Optional[str]=None
    phone:Optional[str]=None
    otp:int

    # @field_validator('email')
    # def validate_email(cls,v):
    #     if v:
    #         EmailStr.validate(v)
    #     return v

    # @field_validator("phone")
    # def validate_phone(cls,v):
    #     if v:
    #         if not re.match(r'^\d{10}$', v):
    #             raise ValueError('Invalid phone number format')
    #     return v

    # @field_validator('otp')
    # def validate_password(cls, v):
    #     if len(v) != 6:
    #         raise ValueError('OTP must be 6 digits long')
    #     return v

class UserResendOTP(BaseModel):
    email:Optional[str]=None
    phone:Optional[str]=None
    
    # @field_validator('email')
    # def validate_email(cls,v):
    #     if v:
    #         EmailStr.validate(v)
    #     return v

    # @field_validator("phone")
    # def validate_phone(cls,v):
    #     if v:
    #         if not re.match(r'^\d{10}$', v):
    #             raise ValueError('Invalid phone number format')
    #     return v