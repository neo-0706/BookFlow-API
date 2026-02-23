from fastapi import FastAPI , Query , File, UploadFile, Form
import os
from typing import  Optional
from fastapi.staticfiles import StaticFiles
import asyncpg
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL)
    print("✅ به دیتابیس PostgreSQL وصل شدم")
    yield
    await app.state.db_pool.close()
    print("✅ از دیتابیس جدا شدم")

app = FastAPI(lifespan=lifespan)
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
async def read_root():
    return {"message" : "Hello"}

@app.post('/create-book')
async def create(id : int = Form(..., ge=1) , title : str =Form(..., min_length=3 , max_length = 100) , file: UploadFile= File(...) , author : str = Form(...)):
    file_path = f"static/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    async with app.state.db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO books (id, title, author , image_url) VALUES ($1 , $2, $3, $4)",
            id , title , author , file_path
        )
    return {"message" : "book successfuly add"}
@app.get('/search')
async def search(q: Optional[str] = Query(None, min_length=3, max_length=100),skip: int= Query(0, ge=0),limit:int=Query(5, le=10)):
    async with app.state.db_pool.acquire() as conn:
        if q:
            rows = await conn.fetch(
                "SELECT * FROM books WHERE title ILIKE $1 OR author ILIKE $1 ORDER BY id LIMIT $2 OFFSET $3",
                f'%{q}%', limit , skip
            )
        else:
            rows = await conn.fetch(
                "SELECT * FROM books ORDER BY id LIMIT $1 OFFSET $2",
                limit , skip
            )
        return [dict(row) for row in rows]


