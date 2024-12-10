from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.post import ArticleCreate, Article
from database.database import get_db
from database.models import Article as ArticleModel  # Ваша модель статьи из базы данных
from api.auth import get_current_user # Для проверки авторизации (если нужно)
from schemas.user import User
import datetime

router = APIRouter(prefix="/articles", tags=["articles"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Article)
def create_article(article: ArticleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)): #Если требуется авторизация
    # Проверьте, авторизован ли пользователь и имеет ли права на создание статьи. Например:
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Forbidden")

    db_article = ArticleModel(**article.dict(), publication_date=datetime.utcnow()) #используем author_id
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


@router.get("/{article_id}", response_model=Article)
def read_article(article_id: int, db: Session = Depends(get_db)):
    db_article = db.query(ArticleModel).filter(ArticleModel.article_id == article_id).first()
    if db_article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return db_article
