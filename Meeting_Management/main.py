from fastapi import FastAPI, BackgroundTasks
from . import models
from .database import engine
from os import path
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost.meetingapi.com",
    "https://localhost.meetingapi.com",
    "http://localhost",
    "http://localhost:8081",
    "http://10.24.52.22/:1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "new-meeting:1", "login:1"],
)

UPLOAD_FOLDER = path.join(app.root_path, 'static', 'uploads')
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

models.Base.metadata.create_all(bind=engine)


from .routers import meeting, person, factory, file, motion, authentication, email

app.include_router(authentication.router)
app.include_router(meeting.router)
app.include_router(person.router)
app.include_router(factory.router)
app.include_router(file.router)
app.include_router(motion.router)
app.include_router(email.router)
