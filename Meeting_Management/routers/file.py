import asyncio
import os
from typing import List
import aiofiles
from fastapi import APIRouter, UploadFile
from ..main import UPLOAD_FOLDER
from ..schemas import Attachment

router = APIRouter(
    prefix='/file',
    tags=['File']
)


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

    return out_file_path


@router.post("/upload/{meeting_id}")
async def upload_files(meeting_id: int, files: List[UploadFile]):
    file_tasks = [upload_file(meeting_id, file) for file in files]

    out_put_paths = await asyncio.gather(*file_tasks, return_exceptions=True)

    return out_put_paths
