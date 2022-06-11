from fastapi import FastAPI
from . import models
from .database import engine
from os import path
from pathlib import Path


app = FastAPI()

UPLOAD_FOLDER = path.join(app.root_path, 'static', 'uploads')
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

models.Base.metadata.create_all(bind=engine)


from .routers import meeting, person, factory, file, motion, authentication

app.include_router(authentication.router)
app.include_router(meeting.router)
app.include_router(person.router)
app.include_router(factory.router)
app.include_router(file.router)
app.include_router(motion.router)
