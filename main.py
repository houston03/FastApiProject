from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.schema import CreateTable
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import Base # Импортируйте Base
from database.models import User, Article # Импортируйте ваши модели
import os


DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:root@localhost:5432/blogapp")

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
            # for table in reversed(Base.metadata.sorted_tables):
            #     await session.execute(CreateTable(table))
            # await session.commit()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)