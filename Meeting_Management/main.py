from fastapi import FastAPI
from . import models
from .database import engine
from .routers import meeting, person, factory

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


app.include_router(meeting.router)
app.include_router(person.router)
app.include_router(factory.router)


