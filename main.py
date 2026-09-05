from fastapi import FastAPI
from routers import authentication, user
from db.database import engine, Base


app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello World"}


app.include_router(authentication.router)
app.include_router(user.router)


Base.metadata.create_all(bind=engine)
