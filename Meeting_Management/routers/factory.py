from typing import List
from fastapi import APIRouter, Depends
from . import person as person_route
from . import meeting as meeting_route
from .. import database, schemas, models, oauth2
from sqlalchemy.orm import Session
from datetime import datetime
from datetime import timedelta
from faker import Faker
import random

router = APIRouter(
    prefix='/factory',
    tags=['Factory']
)

get_db = database.get_db

faker = Faker('zh_TW')


@router.get('/person/{count}', response_model=List[schemas.PersonShow])
def gen_people(count: int, db: Session = Depends(get_db)):

    people = []
    while count:
        person = schemas.Person(name=faker.name(),
                                gender=random.choice(list(models.GenderType)),
                                phone=faker.phone_number(),
                                email=faker.email(),
                                type=random.choice(list(models.PersonType))
                                )

        while db.query(models.Person).filter_by(email=person.email).first():
            person.email = faker.email()

        if person.type == models.PersonType.DeptProf:
            person.dept_prof_info = schemas.Deptprof(job_title=faker.job(),
                                                     office_tel=faker.phone_number())
        elif person.type == models.PersonType.Assistant:
            person.assistant_info = schemas.Assistant(office_tel=faker.phone_number())
        elif person.type == models.PersonType.OtherProf:
            person.other_prof_info = schemas.Otherprof(univ_name="高雄大學",
                                                       dept_name=faker.license_plate(),
                                                       job_title=faker.job(),
                                                       office_tel=faker.phone_number(),
                                                       address=faker.address(),
                                                       bank_account=faker.isbn10()
                                                       )
        elif person.type == models.PersonType.Expert:
            person.expert_info = schemas.Expert(company_name=faker.company(),
                                                job_title=faker.job(),
                                                office_tel=faker.phone_number(),
                                                address=faker.address(),
                                                bank_account=faker.isbn10())
        elif person.type == models.PersonType.Student:
            gen_student_id = 'A' + str(random.randint(100, 115)) + str(random.randint(1000, 9999))
            if db.query(models.Student).filter_by(student_id=gen_student_id).first():
                gen_student_id = 'A' + str(random.randint(100, 115)) + str(random.randint(1000, 9999))
            person.student_info = schemas.Student(
                student_id=gen_student_id,
                program=random.choice(list(models.StudentProgramType)),
                study_year=random.choice(list(models.StudentStudyYearType))
            )
        people.append(person)
        count -= 1

    return people


@router.post('/person/{count}')
def create_people(count: int, db: Session = Depends(get_db)):

    for person in gen_people(count, db):
        person_route.create_person(person, db)# 缺一個 token

    return f"{count} people have created"


@router.get('/meeting/{count}', response_model=List[schemas.Meeting])
def gen_meetings(count: int, db: Session = Depends(get_db)):

    meetings = []
    while count:
        person = db.query(models.Person).all()
        random.shuffle(person)

        meeting = schemas.Meeting(title=faker.sentence(), type=random.choice(list(models.MeetingType)),
                                  time=datetime.utcnow() - timedelta(days=random.randint(0, 7),
                                                                     hours=random.randint(0, 23),
                                                                     minutes=random.randint(0, 59)),
                                  location=faker.address(), chair_id=person.pop().id,
                                  chair_speech=faker.text(), chair_confirmed=faker.boolean(chance_of_getting_true=50),
                                  minute_taker_id=person.pop().id
                                  )

        meeting.attendees = []
        meeting.announcements = []
        meeting.extempores = []
        meeting.motions = []
        for _ in range(random.randrange(2, len(person), 1)):
            attendance = schemas.Attendee(person_id=person.pop().id,
                                          is_present=faker.boolean(chance_of_getting_true=50),
                                          is_confirmed=faker.boolean(chance_of_getting_true=50),
                                          is_member=faker.boolean(chance_of_getting_true=50))
            meeting.attendees.append(attendance)

        for _ in range(random.randint(0, 5)):
            meeting.announcements.append(generate_announcement())

        for _ in range(random.randint(0, 3)):
            meeting.extempores.append(generate_extempore())

        for _ in range(random.randint(1, 3)):
            meeting.motions.append(generate_motion())

        meetings.append(meeting)
        count -= 1

    return meetings


@router.post('/meeting/{count}')
def create_meetings(count: int, db: Session = Depends(get_db)):
    for meetings in gen_meetings(count, db):
        meeting_route.create_meeting(meetings, [], db)

    return f"{count} meetings have created"


def generate_announcement():
    announcement = schemas.Announcement(
        content=faker.paragraph(nb_sentences=random.randint(3, 5)))
    return announcement


def generate_extempore():
    extempore = schemas.Extempore(
        content=faker.paragraph(nb_sentences=random.randint(3, 5)))
    return extempore


def generate_motion():
    motion = schemas.Motion(description=faker.sentence(),
                            content=faker.paragraph(nb_sentences=random.randint(0, 5)),
                            status=random.choice(list(models.MotionStatusType)),
                            resolution=faker.paragraph(nb_sentences=random.randint(0, 3)),
                            execution=faker.paragraph(nb_sentences=random.randint(0, 3))
                            )
    return motion
