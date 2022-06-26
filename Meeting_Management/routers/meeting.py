import asyncio
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from . import file as file_route
from . import authentication
from .. import database, models, schemas, oauth2, JWTtoken
from ..myOuth2 import OAuth2PasswordBearer

router = APIRouter(
    prefix='/meeting',
    tags=['Meetings']
)

get_db = database.get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get('/', response_model=List[schemas.MeetingShow])
def get_current(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()

    attend = db.query(models.Attendee).filter_by(person_id=user.id)
    meetings_main = db.query(models.Meeting).filter(or_(models.Meeting.chair_id.like(user.id),
                                                        models.Meeting.minute_taker_id.like(user.id)))
    meetings = db.query(models.Meeting).join(attend.subquery()).union(meetings_main).order_by(desc(models.Meeting.time))

    print(meetings.all())
    return meetings.all()


@router.get('/all', response_model=List[schemas.MeetingShow])
def get_all(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    # if user.type != '系助理':
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail=f"You have no authorization to get all meetings")

    meetings = db.query(models.Meeting).all()
    return meetings


@router.get('/{id}', response_model=schemas.MeetingShow)
def get_meeting(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    # if user.type != '系助理':
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
    #                         detail=f"You have no authorization to get meetings")

    current_user_email = oauth2.get_current_user
    print(current_user_email)
    meeting = db.query(models.Meeting).get(id)
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Meeting with the id {id} is not available")

    print(meeting.attendee_association)
    return meeting


@router.post('/', response_model=schemas.MeetingShow)
def create_meeting(request: schemas.Meeting, files: List[UploadFile], db: Session = Depends(get_db),
                   token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to create meetings")

    meeting = models.Meeting()
    meeting.title = request.title
    meeting.type = request.type
    meeting.time = request.time
    meeting.location = request.location
    meeting.is_draft = request.is_draft

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

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    asyncio.run(file_route.upload_files(meeting.id, files, db, token))

    return meeting


@router.delete('/{id}')
def delete_meeting(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to delete meetings")

    meeting = db.query(models.Meeting).filter_by(id=id)

    if not meeting.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Meeting with id {id} not found")

    for attachment in meeting.first().attachments:
        file_route.delete_file(attachment.id, db, token)

    meeting.delete(synchronize_session=False)

    db.commit()
    return 'done'


@router.put('/{id}', response_model=schemas.MeetingShow)
def update_meeting(id: int, request: schemas.Meeting, files: List[UploadFile], db: Session = Depends(get_db),
                   token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to update meetings")

    meeting = db.query(models.Meeting).get(id)

    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Meeting with id {id} not found")

    meeting.title = request.title
    meeting.type = request.type
    meeting.time = request.time
    meeting.location = request.location
    meeting.is_draft = request.is_draft

    attendees_id = [att.person_id for att in request.attendees]
    attendees_id.append(request.chair_id)
    attendees_id.append(request.minute_taker_id)
    exist_attendee = db.query(models.Person).filter(models.Person.id.in_(attendees_id)).all()
    exist_id = [attendee.id for attendee in exist_attendee]

    if len(set(attendees_id)) != len(attendees_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person (chair_id, minute_id, attendee_id) is repeat")

    if len(exist_attendee) != len(attendees_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with id {set(attendees_id) - set(exist_id)} not found")

    meeting.chair_id = request.chair_id
    meeting.minute_taker_id = request.minute_taker_id
    meeting.chair_speech = request.chair_speech

    # List Object: clear() and append() update information
    meeting.attendees.clear()
    meeting.announcements.clear()
    meeting.motions.clear()
    meeting.extempores.clear()

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

    asyncio.run(file_route.upload_files(id, files, db, token))
    db.commit()
    db.refresh(meeting)

    return meeting
