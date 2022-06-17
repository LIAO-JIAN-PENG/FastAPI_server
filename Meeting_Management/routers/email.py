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
    chair_id_email = db.query(models.Person).get(meeting.chair_id).email
    chair_id_name = db.query(models.Person).get(meeting.chair_id).name
    minute_taker_id_email = db.query(models.Person).get(meeting.minute_taker_id).email
    minute_taker_id_name = db.query(models.Person).get(meeting.minute_taker_id).name
    attendees = db.query(models.Meeting).get(id).attendees
    email_list = []
    name_list = []
    email_list.append(chair_id_email)
    email_list.append(minute_taker_id_email)
    email_list.append('gold90321@gmail.com')
    name_list.append(chair_id_name)
    name_list.append(minute_taker_id_name)
    name_list.append('高銘宏')
    for attendee in attendees:
        attendee_email = db.query(models.Person).get(attendee.id).email
        attendee_name = db.query(models.Person).get(attendee.id).name
        email_list.append(attendee_email)
        name_list.append(attendee_name)

    meeting_information = []
    meeting_information.append(meeting.title)
    meeting_information.append(meeting.time)
    meeting_information.append(meeting.location)

    await send_email.send_email_async('Hello, you have a upcoming meeting.', email_list,
                                      {'name': name_list, 'meeting_information': meeting_information})
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
    chair_id_email = db.query(models.Person).get(meeting.chair_id).email
    chair_id_name = db.query(models.Person).get(meeting.chair_id).name
    minute_taker_id_email = db.query(models.Person).get(meeting.minute_taker_id).email
    minute_taker_id_name = db.query(models.Person).get(meeting.minute_taker_id).name
    attendees = db.query(models.Meeting).get(id).attendees
    email_list = []
    name_list = []
    email_list.append(chair_id_email)
    email_list.append(minute_taker_id_email)
    email_list.append('gold90321@gmail.com')
    name_list.append(chair_id_name)
    name_list.append(minute_taker_id_name)
    name_list.append('高銘宏')
    for attendee in attendees:
        attendee_email = db.query(models.Person).get(attendee.id).email
        attendee_name = db.query(models.Person).get(attendee.id).name
        email_list.append(attendee_email)
        name_list.append(attendee_name)

    meeting_information = []
    meeting_information.append(meeting.title)
    meeting_information.append(meeting.time)
    meeting_information.append(meeting.location)
    send_email.send_email_background(background_tasks, 'Hello, you have a upcoming meeting.', email_list,
                                     {'name': name_list, 'meeting_information': meeting_information})
    return 'Success'
