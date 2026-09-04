from fastapi import FastAPI
from db.database import engine
from db import database
app = FastAPI()


@app.get('/')
def index():
    return {'message':"Hello World"}



database.Base.metadata.create_all(engine)
