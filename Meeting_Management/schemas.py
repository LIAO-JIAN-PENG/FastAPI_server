from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from fastapi import Form
from . import models
import json


"""
Person
"""


class Expert(BaseModel):
    company_name: str = ""
    job_title: str = ""
    office_tel: str = ""
    address: str = ""
    bank_account: str = ""

    class Config:
        orm_mode = True


class Assistant(BaseModel):
    office_tel: str = ""

    class Config:
        orm_mode = True


class Deptprof(BaseModel):
    job_title: str = ""
    office_tel: str = ""

    class Config:
        orm_mode = True


class Otherprof(BaseModel):
    univ_name: str = ""
    dept_name: str = ""
    job_title: str = ""
    office_tel: str = ""
    address: str = ""
    bank_account: str = ""

    class Config:
        orm_mode = True


class Student(BaseModel):
    student_id: str = ""
    program: models.StudentProgramType
    study_year: models.StudentStudyYearType

    class Config:
        orm_mode = True


class PersonBase(BaseModel):
    name: str
    gender: models.GenderType = models.GenderType.Male
    phone: str
    email: str
    type: models.PersonType = models.PersonType.Expert


class Person(PersonBase):
    expert_info: Optional[Expert] = None
    assistant_info: Optional[Assistant] = None
    dept_prof_info: Optional[Deptprof] = None
    other_prof_info: Optional[Otherprof] = None
    student_info: Optional[Student] = None

    class Config:
        orm_mode = True


class PersonShow(Person):
    def dict(self, *args, **kwargs):
        if kwargs and kwargs.get("exclude_none") is not None:
            kwargs["exclude_none"] = True
            return BaseModel.dict(self, *args, **kwargs)


"""
Meeting
"""


class Attendee(BaseModel):
    person_id: int
    is_present: bool = True
    is_confirmed: bool = False
    is_member: bool = True

    class Config:
        orm_mode = True


class Attachment(BaseModel):
    filename: str
    file_path: str

    class Config:
        orm_mode = True


class Announcement(BaseModel):
    content: str

    class Config:
        orm_mode = True


class Extempore(BaseModel):
    content: str

    class Config:
        orm_mode = True


class Motion(BaseModel):
    description: str
    content: str
    status: models.MotionStatusType
    resolution: str
    execution: str

    class Config:
        orm_mode = True


class MeetingBase(BaseModel):
    title: str
    type: models.MeetingType
    time: datetime
    location: str
    chair_id: int
    chair_speech: str
    chair_confirmed: bool
    minute_taker_id: int


class Meeting(MeetingBase):
    attendees: List[Attendee] = None
    announcements: List[Announcement] = None
    extempores: List[Extempore] = None
    motions: List[Motion] = None

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    class Config:
        orm_mode = True


# TODO: attendee 有問題要解決
class MeetingShow(MeetingBase):
    announcements: List[Announcement] = None
    extempores: List[Extempore] = None
    motions: List[Motion] = None
    attachments: List[Attachment] = None

    class Config:
        orm_mode = True
