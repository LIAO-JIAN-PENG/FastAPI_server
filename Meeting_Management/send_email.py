"""async def send_email_async(email: EmailSchema):



def send_email_background(subject: str, recipients: List[EmailStr], body: dict):
    html = templates.TemplateResponse("email_notice_template.html",
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
    fm.send_message(message)"""
