import asyncio
import os
from typing import List
import aiofiles
from fastapi import APIRouter, UploadFile, Depends, responses
from ..main import UPLOAD_FOLDER
from .. import database, models
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/file',
    tags=['File']
)

get_db = database.get_db


@router.get("/download/{id}")
def download_files(id: int, db: Session = Depends(get_db)):
    attachment = db.query(models.Attachment).filter_by(id=id).first()

    if not attachment:
        return {'message': f'file with id {id} not found'}

    if not os.path.exists(attachment.file_path):
        return {'message': f'file_path with id {id} not exist'}

    return responses.FileResponse(path=attachment.file_path, filename=attachment.filename)


async def upload_file(meeting_id: int, file: UploadFile):
    out_file_path = os.path.join(UPLOAD_FOLDER, str(meeting_id) + '-' + file.filename)
    file_exist = os.path.exists(out_file_path)

    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)

    return {'filename': file.filename, 'file_path': out_file_path, 'old_file': file_exist}


@router.post("/upload/{meeting_id}")
async def upload_files(meeting_id: int, files: List[UploadFile], db: Session = Depends(get_db)):
    # async upload or update file
    file_tasks = [upload_file(meeting_id, file) for file in files]
    file_info = await asyncio.gather(*file_tasks, return_exceptions=True)

    # Add attachment to meeting
    meeting = db.query(models.Meeting).get(meeting_id)
    for info in file_info:
        # do not create exist attachment relationship
        if info['old_file']:
            print(info['file_path'])
            continue

        attachment = models.Attachment(filename=info['filename'],
                                       file_path=info['file_path'])
        meeting.attachments.append(attachment)

    db.commit()
    db.refresh(meeting)

    return file_info


@router.delete("/delete/{id}")
def delete_file(id: int, db: Session = Depends(get_db)):
    attachment = db.query(models.Attachment).filter_by(id=id)

    if not attachment.first():
        return {'message': f'file with id {id} not found'}

    if not os.path.exists(attachment.first().file_path):
        attachment.delete(synchronize_session=False)
        db.commit()
        return {'message': f'file_path with id {id} not exist, and relationship have been deleted'}

    os.remove(attachment.first().file_path)
    attachment.delete(synchronize_session=False)
    db.commit()

    return 'deleted files'
