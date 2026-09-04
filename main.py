from fastapi import FastAPI
from db.database import engine
from db import database
from routers import post
app = FastAPI()


@app.get('/')
def index():
    return {'message':"Hello World"}


app.include_router(post.router)


database.Base.metadata.create_all(engine)

