from typing import List, Optional
from pydantic import BaseModel
from . import models


class Person(BaseModel):
    name: str
    gender: str
    phone: str
    email: str
    type: str
