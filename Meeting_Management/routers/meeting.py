from fastapi import APIRouter, Depends, status, HTTPException
from .. import database, models, schemas
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


@router.get('/{id}', response_model=schemas.Meeting)
def get_meeting(id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).get(id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meeting with the id {id} is not available")

    return meeting


@router.post('/')
def create_meeting(request: schemas.Meeting, db: Session = Depends(get_db)):
    meeting = models.Meeting()
    meeting.title = request.title
    meeting.type = request.type
    meeting.time = request.time
    meeting.location = request.location

    chair_person = db.query(models.Person).filter_by(id=request.chair_id)
    minute_person = db.query(models.Person).filter_by(id=request.minute_taker_id)

    if (not chair_person.first()) or (not minute_person.first()):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with chair_id {request.chair_id} or \
                            minute_taker_id{request.minute_taker_id} not found")

    meeting.chair_id = request.chair_id
    meeting.minute_taker_id = request.minute_taker_id
    meeting.chair_speech = request.chair_speech

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return meeting


@router.delete('/{id}')
def delete_meeting(id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter_by(id=id)

    if not meeting.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Meeting with id {id} not found")

    meeting.delete(synchronize_session=False)
    db.commit()
    return 'done'


@router.put('/{id}')
def update_meeting(id: int, request: schemas.Meeting, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter_by(id=id)

    if not meeting.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Meeting with id {id} not found")

    chair_person = db.query(models.Person).filter_by(id=request.chair_id)
    minute_person = db.query(models.Person).filter_by(id=request.minute_taker_id)

    if (not chair_person.first()) or (not minute_person.first()):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with chair_id {request.chair_id} or minute_taker_id {request.minute_taker_id} not found")

    meeting.update(request)
    db.commit()
    return 'updated'
