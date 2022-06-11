from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, Enum as dbEnum, DateTime, Boolean, ForeignKey, Text
from Meeting_Management.database import Base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref


class GenderType(str, Enum):
    Male = '男'
    Female = '女'


class PersonType(str, Enum):
    Expert = '業界專家'
    Assistant = '系助理'
    DeptProf = '系上教師'
    OtherProf = '校外教師'
    Student = '學生'


class MeetingType(str, Enum):
    DeptAffairs = '系務會議'
    FacultyEvaluation = '系教評會'
    DeptCurriculum = '系課程委員會'
    StudentAffairs = '招生暨學生事務委員會'
    DeptDevelopment = '系發展協會'
    Other = '其他'


class StudentProgramType(str, Enum):
    UnderGraduate = '大學部'
    Graduate = '碩士班'
    PhD = '博士班'


class StudentStudyYearType(str, Enum):
    FirstYear = '一年級'
    SecondYear = '二年級'
    ThirdYear = '三年級'
    ForthYear = '四年級'
    FifthYear = '五年級'
    SixthYear = '六年級'
    SeventhYear = '七年級'


class MotionStatusType(str, Enum):
    InDiscussion = '討論中'
    InExecution = '執行中'
    Closed = '結案'


class Meeting(Base):
    __tablename__ = 'meeting'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    type = Column(dbEnum(MeetingType), nullable=False)
    time = Column(DateTime, nullable=False, default=datetime.utcnow())
    location = Column(String(50), nullable=False)
    is_draft = Column(Boolean, nullable=False, default=True)

    attachments = relationship('Attachment', backref='meeting', cascade='all, delete-orphan')
    announcements = relationship('Announcement', backref='meeting', cascade='all, delete-orphan')
    extempores = relationship('Extempore', backref='meeting', cascade='all, delete-orphan')
    motions = relationship('Motion', backref='meeting', cascade='all, delete-orphan')

    chair_id = Column(Integer, ForeignKey('person.id', ondelete='SET NULL'))
    chair_speech = Column(Text)
    chair_confirmed = Column(Boolean, nullable=False, default=False)
    chair = relationship('Person', foreign_keys=[chair_id], uselist=False, backref='meetings_as_chair')

    minute_taker_id = Column(Integer, ForeignKey('person.id', ondelete='SET NULL'))
    minute_taker = relationship('Person', foreign_keys=[minute_taker_id], uselist=False,
                                backref='meetings_as_minute_taker')

    attendees = association_proxy('attendee_association', 'attendee',
                                  creator=lambda attendee: Attendee(attendee=attendee))

    def __repr__(self):
        return f'<Meeting {self.id} {self.title} {self.type.value}>'

    def attendees_filter_by(self, **kwargs):
        return Person.query.filter_by(**kwargs).join(Attendee).join(Meeting).filter_by(id=self.id)


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    gender = Column(dbEnum(GenderType), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    type = Column(dbEnum(PersonType), nullable=False)

    expert_info = relationship('Expert', backref='basic_info', uselist=False, cascade='all, delete-orphan')
    assistant_info = relationship('Assistant', backref='basic_info', uselist=False, cascade='all, delete-orphan')
    dept_prof_info = relationship('DeptProf', backref='basic_info', uselist=False, cascade='all, delete-orphan')
    other_prof_info = relationship('OtherProf', backref='basic_info', uselist=False, cascade='all, delete-orphan')
    student_info = relationship('Student', backref='basic_info', uselist=False, cascade='all, delete-orphan')

    meetings_as_attendee = association_proxy('attendee_association', 'meeting',
                                             creator=lambda meeting: Attendee(meeting=meeting))

    def is_admin(self):
        return self.email == 'admin@admin'

    def add_expert_info(self, company_name, job_title, office_tel, address, bank_account):
        expert = Expert()
        expert.company_name = company_name
        expert.job_title = job_title
        expert.office_tel = office_tel
        expert.address = address
        expert.bank_account = bank_account
        self.expert_info = expert

    def add_assistant_info(self, office_tel):
        assistant = Assistant()
        assistant.office_tel = office_tel
        self.assistant_info = assistant

    def add_dept_prof_info(self, job_title, office_tel):
        dept_prof = DeptProf()
        dept_prof.job_title = job_title
        dept_prof.office_tel = office_tel
        self.dept_prof_info = dept_prof

    def add_other_prof_info(self, univ_name, dept_name, job_title, office_tel, address, bank_account):
        other_prof = OtherProf()
        other_prof.univ_name = univ_name
        other_prof.dept_name = dept_name
        other_prof.job_title = job_title
        other_prof.office_tel = office_tel
        other_prof.address = address
        other_prof.bank_account = bank_account
        self.other_prof_info = other_prof

    def add_student_info(self, student_id, program, study_year):
        student = Student()
        student.student_id = student_id
        student.program = program
        student.study_year = study_year
        self.student_info = student

    def __repr__(self):
        return f'<Person {self.id} {self.name} {self.type.value}>'


class Attendee(Base):
    __tablename__ = 'attendee'

    meeting_id = Column(Integer, ForeignKey('meeting.id', ondelete='CASCADE'), primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), primary_key=True)
    meeting = relationship(Meeting, backref=backref('attendee_association', cascade='all, delete-orphan'))
    attendee = relationship(Person, backref=backref('attendee_association', cascade='all, delete-orphan'))
    is_present = Column(Boolean, nullable=False, default=False)
    is_confirmed = Column(Boolean, nullable=False, default=False)
    is_member = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f'<Attendee {self.meeting.title} {self.attendee.name}>'


class Expert(Base):
    __tablename__ = 'expert'

    person_id = Column(Integer, ForeignKey('person.id', ondelete="CASCADE"), primary_key=True)
    company_name = Column(String(50), nullable=False)
    job_title = Column(String(50), nullable=False)
    office_tel = Column(String(20))
    address = Column(String(500))
    bank_account = Column(String(50))


class Assistant(Base):
    __tablename__ = 'assistant'

    person_id = Column(Integer, ForeignKey('person.id', ondelete="CASCADE"), primary_key=True)
    office_tel = Column(String(20))


class DeptProf(Base):
    __tablename__ = 'deptProf'

    person_id = Column(Integer, ForeignKey('person.id', ondelete="CASCADE"), primary_key=True)
    job_title = Column(String(50), nullable=False)
    office_tel = Column(String(20))


class OtherProf(Base):
    __tablename__ = 'otherProf'

    person_id = Column(Integer, ForeignKey('person.id', ondelete="CASCADE"), primary_key=True)
    univ_name = Column(String(50), nullable=False)
    dept_name = Column(String(50), nullable=False)
    job_title = Column(String(50), nullable=False)
    office_tel = Column(String(20))
    address = Column(String(500))
    bank_account = Column(String(50))


class Student(Base):
    __tablename__ = 'student'

    person_id = Column(Integer, ForeignKey('person.id', ondelete="CASCADE"), primary_key=True)
    student_id = Column(String(50), nullable=False, unique=True)
    program = Column(dbEnum(StudentProgramType), nullable=False)
    study_year = Column(dbEnum(StudentStudyYearType), nullable=False)


class Attachment(Base):
    __tablename__ = 'attachment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meeting.id', ondelete="CASCADE"), primary_key=True)
    filename = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)

    def __init__(self, filename, file_path):
        self.filename = filename
        self.file_path = file_path

    def __repr__(self):
        return f'<File {self.id} {self.meeting_id} {self.filename}>'


class Announcement(Base):
    __tablename__ = 'announcement'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meeting.id', ondelete="CASCADE"), primary_key=True)
    content = Column(Text, nullable=False)

    def __init__(self, content):
        self.content = content


class Extempore(Base):
    __tablename__ = 'extempore'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meeting.id', ondelete="CASCADE"), primary_key=True)
    content = Column(Text, nullable=False)

    def __init__(self, content):
        self.content = content


class Motion(Base):
    __tablename__ = 'motion'

    id = Column(Integer, primary_key=True, autoincrement=True)
    meeting_id = Column(Integer, ForeignKey('meeting.id', ondelete="CASCADE"), primary_key=True)
    description = Column(Text, nullable=False)
    content = Column(Text)
    status = Column(dbEnum(MotionStatusType), nullable=False, default=MotionStatusType.InDiscussion)
    resolution = Column(Text)
    execution = Column(Text)

    def __init__(self, description, content, status, resolution, execution):
        self.description = description
        self.content = content
        self.status = status
        self.resolution = resolution
        self.execution = execution

    def update(self, description, content, status, resolution, execution):
        self.description = description
        self.content = content
        self.status = status
        self.resolution = resolution
        self.execution = execution
