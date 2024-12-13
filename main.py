from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.database import Base
from database.models import User, Article
import os
from dotenv import load_dotenv
from starlette.responses import HTMLResponse


# Загрузка переменных окружения из .env файла
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in environment variables")

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.auth import router as auth_router
from api.users import router as users_router
from api.articles import router as articles_router

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(articles_router)

@app.on_event("startup")
async def startup():
    async with async_session() as session:
        async with session.begin():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)


@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <!DOCTYPE html>

    <html lang="ru">
    <head>
    
    <meta charset="UTF-8">
    
    <title> FastApiProject</title>
    </head>
    
    <body>
    <p style="font-family: 'Yu Gothic UI Light'">FastApi/Mentor/Anton/Olya</p>
    <a style="font-family: 'Yu Gothic UI Light'" href="/docs#/">Swagger</a>
    <p>Home</p>
    </body>
    
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)