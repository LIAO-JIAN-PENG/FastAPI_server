from typing import List
from fastapi import APIRouter, Depends
from . import person as person_route
from .. import database, schemas, models
from sqlalchemy.orm import Session

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
        person_route.create_person(person, db)

    return f"{count} people have created"

