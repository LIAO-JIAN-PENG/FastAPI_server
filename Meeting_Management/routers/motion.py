from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import database, models, schemas

router = APIRouter(
    prefix='/motion',
    tags=['Motions']
)

get_db = database.get_db


@router.get('/', response_model=List[schemas.Motion])
def get_all(db: Session = Depends(get_db)):
    motions = db.query(models.Motion).all()
    return motions
