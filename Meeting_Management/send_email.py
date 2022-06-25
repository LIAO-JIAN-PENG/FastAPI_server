import os
from fastapi import BackgroundTasks, Request
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from typing import List
from .main import templates


parent_dir_path = os.path.dirname(os.path.realpath(__file__))

conf = ConnectionConfig(
    MAIL_USERNAME="a1085513@mail.nuk.edu.tw",
    MAIL_PASSWORD="gold90218",
    MAIL_FROM="a1085513@mail.nuk.edu.tw",
    MAIL_PORT="587",
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="NUK CSIE Meeting Management",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=parent_dir_path + '/templates'
)


async def send_email_async(subject: str, recipients: List[EmailStr], body: dict):
    html = templates.TemplateResponse("email_template.html",
                                      {'request': Request, 'name': body['name'], 'meeting_title': body['information'][0],
                                       'meeting_time': body['information'][1]
                                          , 'meeting_location': body['information'][2]})
    print(recipients)
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=str(html),
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)


def send_email_background(subject: str, recipients: List[EmailStr], body: dict):
    html = templates.TemplateResponse("email_template.html",
                                      {'request': Request, 'name': body['name'],
                                       'meeting_title': body['information'][0],
                                       'meeting_time': body['information'][1]
                                          , 'meeting_location': body['information'][2]})
    print(recipients)
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=str(html),
        subtype="html"
    )

    fm = FastMail(conf)
    fm.send_message(message)
