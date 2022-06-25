from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, encoders
from .. import database, models, schemas, oauth2
from sqlalchemy.orm import Session
from ..repository import person as person_repository
from ..myOuth2 import OAuth2PasswordBearer

router = APIRouter(
    prefix='/person',
    tags=['Persons']
)

get_db = database.get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get('/', response_model=List[schemas.PersonShow])
def get_all(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    # if user.type != '系助理':
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail=f"You have no authorization to get all person")

    people = person_repository.show_all(db)
    return people


@router.get('/{id}', response_model=schemas.PersonShow)
def get_person(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    # if user.type != '系助理':
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail=f"You have no authorization to get person")

    person = person_repository.show_id(db, id)
    return person


@router.post('/')
def create_person(request: schemas.Person, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to create person")

    person = person_repository.create(request, db)
    return person


@router.delete('/{id}')
def delete_person(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to delete person")

    person_repository.delete(db, id)
    return 'deleted'


@router.put('/{id}')
def update_person(id: int, request: schemas.Person, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to update person")

    person_repository.update(db, id, request)
    return 'updated'
