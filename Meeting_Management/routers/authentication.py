from .. import database, models, JWTtoken, schemas
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from ..myOauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import secrets
router = APIRouter(
    tags=['Authentication']
)

get_db = database.get_db


@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.Person).filter(models.Person.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect email",
                            headers={"WWW-Authenticate": "Basic"})

    access_token = JWTtoken.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
