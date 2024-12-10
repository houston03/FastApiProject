from datetime import datetime
from pydantic import BaseModel
from schemas.user import User # Импортируйте схему User


class ArticleCreate(BaseModel):
    title: str
    category: str
    summary_1: str | None = None
    summary_2: str | None = None
    author_id: int


class Article(BaseModel):
    article_id: int
    title: str
    category: str
    summary_1: str | None = None
    summary_2: str | None = None
    publication_date: datetime
    author: User #Включите User схему

    class Config:
        orm_mode = True