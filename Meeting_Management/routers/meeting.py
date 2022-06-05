import asyncio
import os

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from .. import database, models, schemas
from ..main import UPLOAD_FOLDER
from . import file as file_route
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix='/meeting',
    tags=['Meetings']
)

get_db = database.get_db


@router.get('/', response_model=List[schemas.Meeting])
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
def create_meeting(request: schemas.Meeting, files: List[UploadFile], db: Session = Depends(get_db)):
    meeting = models.Meeting()
    meeting.title = request.title
    meeting.type = request.type
    meeting.time = request.time
    meeting.location = request.location

    attendees_id = [att.person_id for att in request.attendees]
    attendees_id.append(request.chair_id)
    attendees_id.append(request.minute_taker_id)
    exist_attendee = db.query(models.Person).filter(models.Person.id.in_(attendees_id)).all()
    exist_id = [attendee.id for attendee in exist_attendee]

    if len(exist_attendee) != len(attendees_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with id {set(attendees_id) - set(exist_id)} not found")

    meeting.chair_id = request.chair_id
    meeting.minute_taker_id = request.minute_taker_id
    meeting.chair_speech = request.chair_speech

    for item in request.attendees:
        attendee = models.Attendee(person_id=item.person_id,
                                   is_present=item.is_present,
                                   is_confirmed=item.is_confirmed,
                                   is_member=item.is_member)
        meeting.attendee_association.append(attendee)

    for item in request.announcements:
        announcement = models.Announcement(content=item.content)
        meeting.announcements.append(announcement)

    for item in request.motions:
        motion = models.Motion(description=item.description,
                               content=item.content,
                               status=item.status,
                               resolution=item.resolution,
                               execution=item.execution)
        meeting.motions.append(motion)

    for item in request.extempores:
        extempore = models.Extempore(content=item.content)
        meeting.extempores.append(extempore)

    for file in files:
        attachment = models.Attachment(filename=file.filename,
                                       file_path=os.path.join(UPLOAD_FOLDER, str(meeting.id) + '-' + file.filename))
        meeting.attachments.append(attachment)

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    asyncio.run(file_route.upload_files(meeting.id, files))

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
                            detail=f"Person with id {request.chair_id}, {request.minute_taker_id} not found")

    meeting.update(request)
    db.commit()
    return 'updated'
