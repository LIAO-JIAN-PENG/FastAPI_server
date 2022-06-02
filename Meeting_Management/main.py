from fastapi import FastAPI
from . import models
from .database import engine
from .routers import meeting, person

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get('/')
def home():
    return 'hello'


app.include_router(meeting.router)
app.include_router(person.router)


