from fastapi import FastAPI

from app.routers import auth, users

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "Simple User API is running"}
