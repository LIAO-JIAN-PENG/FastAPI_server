import asyncio
import os
from typing import List
import aiofiles
from fastapi import APIRouter, UploadFile, Depends
from ..main import UPLOAD_FOLDER
from .. import database, models
from sqlalchemy.orm import Session

router = APIRouter(
    prefix='/file',
    tags=['File']
)

get_db = database.get_db

# @router.get("/download/{meeting_id}")
# async def download_files(meeting_id: int, files: List[UploadFile]):
#     for file in files:
#         out_file_path = os.path.join(UPLOAD_FOLDER, str(meeting_id) + '-' + file.filename)
#
#         async with aiofiles.open(out_file_path, 'wb') as out_file:
#             content = await file.read()  # async read
#             await out_file.write(content)
#
#     return {"filenames": [file.filename for file in files]}


async def upload_file(meeting_id: int, file: UploadFile):
    out_file_path = os.path.join(UPLOAD_FOLDER, str(meeting_id) + '-' + file.filename)

    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)

    return {'filename': file.filename, 'file_path': out_file_path}


@router.post("/upload/{meeting_id}")
async def upload_files(meeting_id: int, files: List[UploadFile], db: Session = Depends(get_db)):
    file_tasks = [upload_file(meeting_id, file) for file in files]

    file_info = await asyncio.gather(*file_tasks, return_exceptions=True)

    meeting = db.query(models.Meeting).get(meeting_id)

    for info in file_info:
        attachment = models.Attachment(filename=info['filename'],
                                       file_path=info['file_path'])
        meeting.attachments.append(attachment)

    db.commit()
    db.refresh(meeting)

    return file_info
