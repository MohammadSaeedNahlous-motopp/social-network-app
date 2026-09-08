from fastapi import FastAPI

from db.seed import seed_group_roles
from routers import authentication, user, group, group_member, post
from db.database import engine, Base, SessionLocal

app = FastAPI()


@app.get("/")
def index():
    return {"message": "Hello World"}


app.include_router(post.router)

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(group.router)
app.include_router(group_member.router)


Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    seed_group_roles(db)