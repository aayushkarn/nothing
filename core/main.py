from fastapi import FastAPI, Depends, HTTPException
import jwt
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from authToken import Token, create_access_token, create_refresh_token
from database.db_models import User
from database.database import Base, engine, SessionLocal, get_db
from utils import hash_password, validate_email, validate_password, validate_phone
import config
from verification import generate_verification_code
from models.pydantic_models import UserRegistration, UserLogin, UserResendOTP, UserVerification

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/login")
async def login(userLogin:UserLogin, db:Session = Depends(get_db)):
    email = userLogin.email
    phone = userLogin.phone
    password = userLogin.password

    if email and phone:
        raise HTTPException(status_code=400, detail="Email and phone cannot be provided together")
    if not email and not phone:
        raise HTTPException(status_code=400, detail="Email or phone not provided")
    if email and not phone:
        user = db.query(User).filter(User.email == email).first()
    elif phone and not email:
        user = db.query(User).filter(User.phone == phone).first()
    else:
        raise HTTPException(status_code=400, detail="Email and Phone cannot be used at once")

    if user is None:
        raise HTTPException(status_code=400, detail="Invalid Login Credentials!")
    
    if user.is_verified != 1:
        raise HTTPException(status_code=400, detail="User not verified. You need to be verified to login")
    
    if user.password is None:
        raise HTTPException(status_code=400, detail="Password cannot be empty")
    
    user_password = validate_password(user.password, password)
    if user_password:
        user_id = {"id":user.id}
        access_token = create_access_token(data=user_id)
        refresh_token = create_refresh_token(data=user_id)

        return {"message":"Login Successful.","access_token":access_token, "refresh_token":refresh_token, "token_type":"bearer"}
    else:
        return {"message":"Invalid username/password"}




@app.post("/register")
async def register(user:UserRegistration, db:Session = Depends(get_db)):
    if user.email and user.phone:
        raise HTTPException(status_code=400, detail="Email and phone cannot be provided at once")
    if user.email:
        print("here")
        if not validate_email(user.email):
            raise HTTPException(status_code=400, detail="Email Invalid")
        existing_user = db.query(User).filter(User.email == user.email).first()
    if user.phone:
        if not validate_phone(user.phone) or not user.phone.isnumeric():
            raise HTTPException(status_code=400, detail="Phone must be of 10 digits")
        existing_user = db.query(User).filter(User.phone == user.phone).first()
    existing_business_ein = db.query(User).filter(User.business_ein == user.business_ein).first()
    # print(existing_user)
    #TODO: Before checking they already exist we check if they are verified or not. Incase a phone/email exists and is not verified we dont raise an error but just redirect user to verification page
    if existing_user and existing_user.is_verified == 0:
        raise HTTPException(status_code=400, detail="User with this email/phone already exists but is not verified yet.")
    
    if existing_business_ein:
        raise HTTPException(status_code=400, detail="A business with same EIN already exists!")

    if existing_user:
        raise HTTPException(status_code=400, detail="Email or Phone already exists!")
    
    if len(user.password)<8:
        raise HTTPException(status_code=400, detail="Password must be more than 8 characters")
    
    hashed_password = hash_password(user.password)
    temp_otp =generate_verification_code()

    new_user = User(
        email = user.email,
        phone = user.phone,
        password = hashed_password,
        business_ein = user.business_ein,
        business_name = user.business_name,
        verification_code = temp_otp,
        verification_sent_at = datetime.now(timezone.utc)
    )

    # TODO: Send verification code to user

    db.add(new_user)
    db.commit()
    
    return {"message":"Registration Successful. Please check email/SMS for OTP.", "TEMP_OTP":temp_otp}


# Takes user email or phone that they just registered with
@app.post("/verify")
async def verify_user(verificationModel:UserVerification ,db:Session = Depends(get_db)):
    email = verificationModel.email
    phone = verificationModel.phone
    otp = verificationModel.otp

    if not email and not phone:
        raise HTTPException(status_code=400, detail="Email or phone not provided")
    if email and phone:
        raise HTTPException(status_code=400, detail="Email and phone cannot be provided at once")
    if email:
        if not validate_email(email):
            raise HTTPException(status_code=400, detail="Email Invalid")
        user = db.query(User).filter(User.email == email).first()
    if phone:
        if not validate_phone(phone) or not phone.isnumeric():
            raise HTTPException(status_code=400, detail="Phone must be of 10 digits")
        user = db.query(User).filter(User.phone == phone).first()
    
    
    if user is None:
        raise HTTPException(status_code=400, detail="User with this email/phone not found!")
    
    if user.is_verified == 1:
        raise HTTPException(status_code=400, detail="User already verified!")
    
    verification_code = user.verification_code
    verification_sent_at = user.verification_sent_at

    if not verification_code:
        raise HTTPException(status_code=400, detail="No verification code for the user!")
    if verification_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    verification_sent_at = verification_sent_at.replace(tzinfo=timezone.utc)
    if verification_sent_at + timedelta(seconds=config.VERIFICATION_EXPIRY_TIME) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP already expired!")
    
    user.is_verified = 1
    db.commit()
    db.refresh(user)

    user_data = {"id":user.id}
    access_token = create_access_token(data=user_data)
    refresh_token = create_refresh_token(data=user_data)

    return {"message":"Registration Successful. You are now registered.","access_token":access_token, "refresh_token":refresh_token, "token_type":"bearer"}


@app.post("/resend_otp")
async def resend_otp(resendModel:UserResendOTP ,db:Session = Depends(get_db)):
    email = resendModel.email
    phone = resendModel.phone

    # TODO: Add a limit to resend otp
    if not email and not phone:
        raise HTTPException(status_code=400, detail="Email or phone not provided")
    if email and phone:
        raise HTTPException(status_code=400, detail="Email and phone cannot be provided at once")
    
    if email:
        if not validate_email(email):
            raise HTTPException(status_code=400, detail="Email Invalid")
        user = db.query(User).filter(User.email == email).first()
    if phone:
        if not validate_phone(phone) or not phone.isnumeric():
            raise HTTPException(status_code=400, detail="Phone must be of 10 digits")
        user = db.query(User).filter(User.phone == phone).first()
    if user is None:
        raise HTTPException(status_code=400, detail="User with this email/phone not found!")
    
    # Incase the OTP is not expired do nothing
    if user.verification_code:
        if user.verification_sent_at + timedelta(seconds=config.VERIFICATION_EXPIRY_TIME) > datetime.now():
            return {"message":"OTP sent to email/phone."}
    
    user.verification_code = generate_verification_code()
    user.verification_sent_at = datetime.now(timezone.utc)

    db.commit()
    return {"message":"OTP sent to email/phone."}


@app.post("/refresh",response_model=Token)
async def refresh_access_token(refresh_token:str):
    try:
        # decode refresh token
        payload = jwt.decode(refresh_token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Invalid refresh token")
        # generate new access token
        user_data = {"id":user_id}
        access_token = create_access_token(data=user_data)

        #we are providing new refresh token with new access token
        new_refresh_token = create_refresh_token(data=user_data)
        return {"access_token":access_token,"refresh_token":new_refresh_token, "token_type":"bearer"}
        
    except jwt.DecodeError:
        raise HTTPException(status_code=403, detail="Token is invalid.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Refresh token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=403, detail="Invalid refresh token")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
