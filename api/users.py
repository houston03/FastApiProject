from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from schemas.user import UserCreate, User
from database.database import get_db
from database.models import User as UserModel
from api.auth import get_current_user, create_access_token # Импортируйте create_access_token
import bcrypt
import yagmail
import os

router = APIRouter(prefix="/users", tags=["users"])

# Замените на ваши данные для отправки почты
YAGMAIL_USER = os.environ.get("Yandex_User")
YAGMAIL_PASSWORD = os.environ.get("Yandex_Password")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = UserModel(username=user.username, email=user.email, password=hashed_password, phone_number=user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Генерация JWT тут
    access_token = create_access_token(data={"sub": db_user.username})

    # Отправка письма в фоновом режиме тут
    background_tasks.add_task(send_confirmation_email, db_user.email, access_token)

    return db_user


@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


def send_confirmation_email(email, access_token):
    yag = yagmail.SMTP(YAGMAIL_USER, YAGMAIL_PASSWORD)
    subject = "Подтверждение регистрации"
    body = f"""
    Спасибо за регистрацию!
    КОД ДОСТУПА: {access_token}
    """
    yag.send(to=email, subject=subject, contents=body)