from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from .. import database, models, schemas
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/person',
    tags=['Persons']
)

get_db = database.get_db


@router.get('/')
def get_all(db: Session = Depends(get_db)):
    people = db.query(models.Person).all()
    return people


@router.get('/{id}', response_model=schemas.Person)
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

    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.delete('/{id}')
def delete_person(id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter_by(id=id)

    if not person.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with id {id} not found")

    person.delete(synchronize_session=False)
    db.commit()
    return 'done'


@router.put('/{id}')
def update_person(id: int, request: schemas.Person, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter_by(id=id)

    if not person.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with id {id} not found")

    person.update(request.dict())
    db.commit()
    return 'updated'
