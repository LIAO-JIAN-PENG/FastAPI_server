from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from .. import database, models, schemas, oauth2
from ..myOuth2 import OAuth2PasswordBearer

router = APIRouter(
    prefix='/motion',
    tags=['Motions']
)

get_db = database.get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get('/', response_model=List[schemas.Motion])
def get_current(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理' and user.email != 'admin@admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to get all motions")

    attend = db.query(models.Attendee).filter_by(person_id=user.id)
    meetings_main = db.query(models.Meeting).filter(or_(models.Meeting.chair_id.like(user.id),
                                                        models.Meeting.minute_taker_id.like(user.id)))
    meetings = db.query(models.Meeting).join(attend.subquery()).union(meetings_main).order_by(desc(models.Meeting.time))

    motions = db.query(models.Motion).join(meetings.subquery()).order_by(models.Motion.status).all()

    return motions
