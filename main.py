from fastapi import FastAPI
from routers import post, friend_request, friend, group
from routers import authentication, user
from db.database import engine, Base


app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello World"}


app.include_router(post.router)
app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(friend_request.router)
app.include_router(friend.router)
app.include_router(group.router)


Base.metadata.create_all(bind=engine)
