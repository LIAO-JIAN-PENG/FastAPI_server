from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from .. import database, send_email, models, oauth2
from sqlalchemy.orm import Session
from ..myOuth2 import OAuth2PasswordBearer

router = APIRouter(
    prefix='/email',
    tags=['email']
)

get_db = database.get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get('/{id}/asynchronous')
async def send_email_asynchronous(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理' and user.email != 'admin@admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to get meetings")

    meeting = db.query(models.Meeting).get(id)
    if meeting.first() == null:
        return 'empty mail'
    attendees = db.query(models.Attendee).filter_by(meeting_id=id)
    names = [att.name for att in meeting.attendees] + [meeting.chair.name] + [meeting.minute_taker.name]
    recipients = [att.email for att in meeting.attendees] + [meeting.chair.email] + [meeting.minute_taker.email]

    information = [meeting.title, meeting.time, meeting.location]

    await send_email.send_email_async('Hello, you have a upcoming meeting.', recipients,
                                      {'name': names, 'information': information})
    return 'Success'


@router.get('/{id}/backgroundtasks')
def send_email_backgroundtasks(background_tasks: BackgroundTasks, id: int, db: Session = Depends(get_db),
                               token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理' and user.email != 'admin@admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to get meetings")

    meeting = db.query(models.Meeting).get(id)
    if meeting.first() == null:
        return 'empty mail'
    attendees = db.query(models.Attendee).filter_by(meeting_id=id)
    names = [att.name for att in meeting.attendees] + [meeting.chair.name] + [meeting.minute_taker.name]
    recipients = [att.email for att in meeting.attendees] + [meeting.chair.email] + [meeting.minute_taker.email]

    information = [meeting.title, meeting.time, meeting.location]

    send_email.send_email_background(background_tasks, 'Hello, you have a upcoming meeting.', recipients,
                                     {'name': names, 'information': information})
    return 'Success'
