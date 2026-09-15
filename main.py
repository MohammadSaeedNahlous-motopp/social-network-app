from fastapi import FastAPI
from websocket.chat import router as websocket_router
from db.seed import seed_group_roles
from routers import (
    authentication,
    user,
    group,
    group_member,
    post,
    friend_request,
    friend,
    post_group,
    chat,
    message,
)
from db.database import engine, Base, SessionLocal
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/test", StaticFiles(directory="static", html=True), name="test")


@app.get("/")
def index():
    return {"message": "Hello World"}


app.include_router(post.router)
app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(friend_request.router)
app.include_router(friend.router)
app.include_router(group.router)
app.include_router(group_member.router)
app.include_router(post_group.router)
app.include_router(websocket_router)
app.include_router(chat.router)
app.include_router(message.router)

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_group_roles(db)
