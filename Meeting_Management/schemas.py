from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from . import models


class ExpertBase(BaseModel):
    company_name: str = ""
    job_title: str = ""
    office_tel: str = ""
    address: str = ""
    bank_account: str = ""


class AssistantBase(BaseModel):
    office_tel: str = ""


class DeptprofBase(BaseModel):
    job_title: str = ""
    office_tel: str = ""


class OtherprofBase(BaseModel):
    univ_name: str = ""
    dept_name: str = ""
    job_title: str = ""
    office_tel: str = ""
    address: str = ""
    bank_account: str = ""


class StudentBase(BaseModel):
    student_id: str = ""
    program: models.StudentProgramType
    study_year: models.StudentStudyYearType


class Expert(ExpertBase):

    class Config:
        orm_mode = True


class Assistant(AssistantBase):

    class Config:
        orm_mode = True


class Deptprof(DeptprofBase):

    class Config:
        orm_mode = True


class Otherprof(OtherprofBase):

    class Config:
        orm_mode = True


class Student(StudentBase):

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


class Meeting(BaseModel):
    title: str
    type: models.MeetingType
    time: datetime
    location: str
    chair_id: int
    chair_speech: str
    chair_confirmed: bool
    minute_taker_id: int

    class Config:
        orm_mode = True

