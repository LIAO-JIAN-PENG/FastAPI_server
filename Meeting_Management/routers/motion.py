from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, schemas, oauth2
from ..myOuth2 import OAuth2PasswordBearer

router = APIRouter(
    prefix='/motion',
    tags=['Motions']
)

get_db = database.get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get('/', response_model=List[schemas.Motion])
def get_all(db: Session = Depends(get_db), current_user: schemas.Person = Depends(oauth2.get_current_user),
            token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理' and user.email != 'admin@admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to get all motions")

    motions = db.query(models.Motion).all()
    return motions
