from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, User
from database.database import get_db
from database.models import User as UserModel
from api.auth import get_current_user, create_access_token
import bcrypt
import logging
from tasks import send_confirmation_email

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(__name__)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db), background_tasks: BackgroundTasks = BackgroundTasks()):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    hashed_password_str = hashed_password.decode('utf-8')  # Преобразуем байты в строку
    db_user = UserModel(username=user.username, email=user.email, password=hashed_password_str, phone_number=user.phone_number)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Генерация JWT тут
    access_token = create_access_token(data={"sub": db_user.username})
    logger.debug(f"Generated JWT Token for user {db_user.username}: {access_token}")  # Добавьте эту строку для логирования токена

    # Отправка письма в фоновом режиме тут
    background_tasks.add_task(send_confirmation_email.delay, db_user.email, access_token)

    return db_user

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
