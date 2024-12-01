import os
import sys
import uvicorn

from fastapi import FastAPI
from app.routers import user_router, question_router, trivia_router, trivia_user_router, trivia_question_router

app = FastAPI()

VERSION_API = "/api/v1"

app.include_router(user_router.router, prefix=VERSION_API, tags=["users"])
app.include_router(question_router.router, prefix=VERSION_API, tags=["questions"])
app.include_router(trivia_router.router, prefix=VERSION_API, tags=["trivias"])
app.include_router(trivia_user_router.router, prefix=VERSION_API, tags=["trivias"])
app.include_router(trivia_question_router.router, prefix=VERSION_API, tags=["trivias"])

@app.get("/")
def root():
    return "Server is running!"

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

