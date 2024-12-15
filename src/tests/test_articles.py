import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.database import Base, get_db
from app.database.models import Article as ArticleModel
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("TEST_DATABASE_URL is not set in environment variables")

engine = create_async_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest.fixture(scope="module")
async def db():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="module")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        await db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.mark.asyncio
async def test_create_article(client, db):
    article_data = {
        "title": "Test Article",
        "content": "This is a test article",
        "author_id": 1
    }
    response = await client.post("/articles/", json=article_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == article_data["title"]
    assert data["content"] == article_data["content"]

@pytest.mark.asyncio
async def test_read_article(client, db):
    article = ArticleModel(title="Test Article", content="This is a test article", author_id=1)
    db.add(article)
    await db.commit()
    await db.refresh(article)

    response = await client.get(f"/articles/{article.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == article.title
    assert data["content"] == article.content

@pytest.mark.asyncio
async def test_search_articles(client, db):
    article = ArticleModel(title="Test Article", content="This is a test article", author_id=1)
    db.add(article)
    await db.commit()
    await db.refresh(article)

    response = await client.get("/articles/search/?query=test")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == article.title
