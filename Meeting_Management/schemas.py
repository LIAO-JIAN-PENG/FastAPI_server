from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from . import models


class Person(BaseModel):
    name: str
    gender: models.GenderType = models.GenderType.Male
    phone: str
    email: str
    type: models.PersonType = models.PersonType.Expert

    class Config:
        orm_mode = True


class Meeting(BaseModel):
    title: str
    type: models.MeetingType
    time: datetime
    location: str
    # is_draft: bool
    chair_id: int
    chair_speech: str
    chair_confirmed: bool
    minute_taker_id: int

    class Config:
        orm_mode = True


