from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, encoders
from .. import database, models, schemas
from sqlalchemy.orm import Session
from ..repository import person as person_repository

router = APIRouter(
    prefix='/person',
    tags=['Persons']
)

get_db = database.get_db


@router.get('/', response_model=List[schemas.PersonShow])
def get_all(db: Session = Depends(get_db)):
    people = person_repository.show_all(db)
    return people


@router.get('/{id}', response_model=schemas.PersonShow)
def get_person(id: int, db: Session = Depends(get_db)):
    person = person_repository.show_id(db, id)
    return person


@router.post('/')
def create_person(request: schemas.Person, db: Session = Depends(get_db)):
    person = person_repository.create(request, db)
    return person


@router.delete('/{id}')
def delete_person(id: int, db: Session = Depends(get_db)):
    person_repository.delete(db, id)
    return 'deleted'


@router.put('/{id}')
def update_person(id: int, request: schemas.Person, db: Session = Depends(get_db)):
    person_repository.update(db, id, request)
    return 'updated'
