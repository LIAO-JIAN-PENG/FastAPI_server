from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, encoders
from .. import database, models, schemas
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/person',
    tags=['Persons']
)

get_db = database.get_db


@router.get('/', response_model=List[schemas.PersonShow])
def get_all(db: Session = Depends(get_db)):
    people = db.query(models.Person).all()
    return people


@router.get('/{id}', response_model=schemas.PersonShow)
def get_person(id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).get(id)

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Person with the id {id} is not available")

    return person


@router.post('/')
def create_person(request: schemas.Person, db: Session = Depends(get_db)):
    person = models.Person()
    person.name = request.name
    person.gender = request.gender
    person.phone = request.phone
    person.email = request.email
    person.type = request.type

    if db.query(models.Person).filter_by(email=person.email).first():
        return encoders.jsonable_encoder({'message': 'Current email has already used'})

    if person.type == models.PersonType.DeptProf:
        person.add_dept_prof_info(
            job_title=request.dept_prof_info.job_title,
            office_tel=request.dept_prof_info.office_tel
        )
    elif person.type == models.PersonType.Assistant:
        person.add_assistant_info(
            office_tel=request.assistant_info.office_tel
        )
    elif person.type == models.PersonType.OtherProf:
        person.add_other_prof_info(
            univ_name=request.other_prof_info.univ_name,
            dept_name=request.other_prof_info.dept_name,
            job_title=request.other_prof_info.job_title,
            office_tel=request.other_prof_info.office_tel,
            address=request.other_prof_info.address,
            bank_account=request.other_prof_info.bank_account
        )
    elif person.type == models.PersonType.Expert:
        person.add_expert_info(
            company_name=request.expert_info.company_name,
            job_title=request.expert_info.job_title,
            office_tel=request.expert_info.office_tel,
            address=request.expert_info.address,
            bank_account=request.expert_info.bank_account)
    elif person.type == models.PersonType.Student:
        if db.query(models.Student).filter_by(student_id=request.student_info.student_id).first():
            return encoders.jsonable_encoder({'message': 'Student ID already exists'})
        person.add_student_info(
            student_id=request.student_info.student_id,
            program=request.student_info.program,
            study_year=request.student_info.study_year
        )

    db.add(person)
    db.commit()
    db.refresh(person)
    return person


# TODO: Delete Still have problem
@router.delete('/{id}')
def delete_person(id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter_by(id=id)

    if not person.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with id {id} not found")

    db.delete(person)
    db.commit()
    return 'deleted'


@router.put('/{id}')
def update_person(id: int, request: schemas.Person, db: Session = Depends(get_db)):
    person = db.query(models.Person).get(id)

    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with id {id} not found")

    person.name = request.name
    person.gender = request.gender
    person.phone = request.phone

    exist_email = db.query(models.Person).filter_by(email=request.email).first()
    if exist_email and exist_email.email != person.email:
        return encoders.jsonable_encoder({'message': 'Current email has already used'})

    person.email = request.email

    if person.type == models.PersonType.Expert:
        db.query(models.Expert).filter_by(person_id=person.id).delete(synchronize_session=False)
    elif person.type == models.PersonType.Assistant:
        db.query(models.Assistant).filter_by(person_id=person.id).delete(synchronize_session=False)
    elif person.type == models.PersonType.DeptProf:
        db.query(models.DeptProf).filter_by(person_id=person.id).delete(synchronize_session=False)
    elif person.type == models.PersonType.OtherProf:
        db.query(models.OtherProf).filter_by(person_id=person.id).delete(synchronize_session=False)
    elif person.type == models.PersonType.Student:
        db.query(models.Student).filter_by(person_id=person.id).delete(synchronize_session=False)

    person.type = request.type

    if person.type == models.PersonType.DeptProf:
        person.add_dept_prof_info(
            job_title=request.dept_prof_info.job_title,
            office_tel=request.dept_prof_info.office_tel
        )
    elif person.type == models.PersonType.Assistant:
        person.add_assistant_info(
            office_tel=request.assistant_info.office_tel
        )
    elif person.type == models.PersonType.OtherProf:
        person.add_other_prof_info(
            univ_name=request.other_prof_info.univ_name,
            dept_name=request.other_prof_info.dept_name,
            job_title=request.other_prof_info.job_title,
            office_tel=request.other_prof_info.office_tel,
            address=request.other_prof_info.address,
            bank_account=request.other_prof_info.bank_account
        )
    elif person.type == models.PersonType.Expert:
        person.add_expert_info(
            company_name=request.expert_info.company_name,
            job_title=request.expert_info.job_title,
            office_tel=request.expert_info.office_tel,
            address=request.expert_info.address,
            bank_account=request.expert_info.bank_account)
    elif person.type == models.PersonType.Student:
        if db.query(models.Student).filter_by(student_id=request.student_info.student_id).first():
            return encoders.jsonable_encoder({'message': 'Student ID already exists'})
        person.add_student_info(
            student_id=request.student_info.student_id,
            program=request.student_info.program,
            study_year=request.student_info.study_year
        )

    db.commit()
    return 'updated'
