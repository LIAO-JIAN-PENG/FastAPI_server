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
    meetings = db.query(models.Person).all()
    return meetings


@router.get('/{id}')
def get_person(id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).filter_by(id=id)
    return person


@router.post('/', response_model=schemas.Person)
def create_person(request: schemas.Person, db: Session = Depends(get_db)):
    person = models.Person(request)
    db.add(person)
    db.commit()
    db.refresh()
    return person
