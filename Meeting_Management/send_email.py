import os
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig


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


async def send_email_async(subject: str, email_to: list, body: dict):
    names = []
    names = body['name']
    meeting_information = []
    meeting_information = body['meeting_information']
    i = 0
    for name in names:
        message = MessageSchema(
            subject=subject,
            recipients=[email_to[i]],
            #body='hello, everyone', # 可以傳入文字區域的string
            # 傳入html區域的變數
            template_body={'name': name, 'meeting_title': meeting_information[0], 'meeting_time': meeting_information[1]
                           , 'meeting_location': meeting_information[2]},
            subtype='html',
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
        i = i + 1


def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: list, body: dict):
    names = []
    names = body['name']
    meeting_information = []
    meeting_information = body['meeting_information']
    i = 0
    for name in names:
        message = MessageSchema(
            subject=subject,
            recipients=[email_to[i]],
            # body='hello, everyone', # 可以傳入文字區域的string
            # 傳入html區域的變數
            template_body={'name': name, 'meeting_title': meeting_information[0], 'meeting_time': meeting_information[1]
                           , 'meeting_location': meeting_information[2]},
            subtype='html',
        )
        fm = FastMail(conf)
        background_tasks.add_task(fm.send_message, message, template_name='email_template.html')
        i = i + 1
