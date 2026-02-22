from fastapi import FastAPI , Query , File, UploadFile, Form
import shutil
import os
from pydantic import BaseModel , Field
from typing import List , Optional
from fastapi.staticfiles import StaticFiles

app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/')
async def read_root():
    return {"message" : "Hello"}
Books=[]

class Book (BaseModel):
    id : int
    title : str = Field (... , min_length= 3 , max_length=100 )
    author : str
    image_url : str

@app.post('/create-book')
async def create(id : int = Form(..., ge=1) , title : str =Form(..., min_length=3 , max_length = 100) , file: UploadFile= File(...) , author : str = Form(...)):
    file_path = f"static/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    new_book = Book(
        id = id ,
        title = title,
        author = author,
        image_url= file_path
    )
    Books.append(new_book)
    return {"message" : "book successfuly add"}
@app.get('/search')
async def search(q: Optional[str] = Query(None, min_length=3, max_length=100),skip: int= Query(0, ge=0),limit:int=Query(5, le=10)):
    results: List = []
    if q == None:
        results = Books
    else :
        for book in Books :
            if q.lower() in book.title.lower() or  q.lower() in book.author.lower() :
                results.append(book)
    return results[skip : skip + limit]


