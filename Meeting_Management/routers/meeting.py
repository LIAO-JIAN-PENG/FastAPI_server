from fastapi import APIRouter, Depends, status, HTTPException
from .. import database, models
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/meeting',
    tags=['Meetings']
)

get_db = database.get_db


@router.get('/')
def get_all(db: Session = Depends(get_db)):
    meetings = db.query(models.Meeting).all()
    return meetings
