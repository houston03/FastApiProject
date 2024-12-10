import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import bcrypt
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


from database.database import get_db
from schemas.user import User
from schemas.authuser import UserAuth
from database.models import User as UserModel

router = APIRouter(prefix="/auth", tags=["authentication"])

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    try:
        logger.debug(f"Plain password: {plain_password}")
        logger.debug(f"Hashed password from DB: {hashed_password}")
        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        logger.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.exception(f"Ошибка в verify_password: {e}")
        return False

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
        user = db.query(UserModel).filter(UserModel.username == token_data).first()
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user


@router.post("/token", response_model=UserAuth)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer", "user": user}
    except Exception as e:
        logger.exception(f"Ошибка в login_for_access_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )