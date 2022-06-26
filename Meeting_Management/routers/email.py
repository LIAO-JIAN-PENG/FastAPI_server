import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from .. import database, models, oauth2
from sqlalchemy.orm import Session
from ..myOuth2 import OAuth2PasswordBearer

parent_dir_path = os.path.dirname(os.path.dirname(__file__))

conf = ConnectionConfig(
    MAIL_USERNAME="a1085513@mail.nuk.edu.tw",
    MAIL_PASSWORD="Gold789123",
    MAIL_FROM="a1085513@mail.nuk.edu.tw",
    MAIL_PORT="587",
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="NUK CSIE Meeting Management",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=parent_dir_path + '/templates'
)

router = APIRouter(
    prefix='/email',
    tags=['email']
)

get_db = database.get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get('/SendMeetingNotice/{id}')
async def send_email_notice(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to get meetings")

    meeting = db.query(models.Meeting).get(id)
    if not meeting:
        return 'empty mail'
    attendees = db.query(models.Attendee).filter_by(meeting_id=id)
    chair = [meeting.chair.name]
    minute_taker = [meeting.minute_taker.name]
    recipients = [att.email for att in meeting.attendees] + [meeting.chair.email] + [meeting.minute_taker.email]

    information = [meeting.title, meeting.time, meeting.location]

    message = MessageSchema(
        subject="You hava a upcoming meeting",
        recipients=recipients,
        template_body={'information': information, 'attendees': attendees, 'chair': chair, 'minute_taker': minute_taker}
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_notice_template.html")

    return 'Success'


@router.get('/SendMeetingResult/{id}')
async def send_email_result(id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user_email = oauth2.get_current_user(token=token)
    user = db.query(models.Person).filter(models.Person.email == current_user_email).first()
    if user.type != '系助理':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"You have no authorization to get meetings")

    meeting = db.query(models.Meeting).get(id)
    if not meeting:
        return 'empty mail'
    attendees = db.query(models.Attendee).filter_by(meeting_id=id)
    chair = [meeting.chair.name]
    minute_taker = [meeting.minute_taker.name]
    recipients = [att.email for att in meeting.attendees] + [meeting.chair.email] + [meeting.minute_taker.email]
    information = [meeting.title, meeting.time, meeting.location, meeting.chair_speech]
    announcements = db.query(models.Announcement).filter_by(meeting_id=id)
    extempores = db.query(models.Extempore).filter_by(meeting_id=id)
    motions = db.query(models.Motion).filter_by(meeting_id=id)

    message = MessageSchema(
        subject="The meeting result is here",
        recipients=recipients,
        template_body={'information': information, 'attendees': attendees, 'chair': chair, 'minute_taker': minute_taker,
                       'announcements': announcements, 'extempores': extempores, 'motions': motions}
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="email_result_template.html")

    return 'Success'
