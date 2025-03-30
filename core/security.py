import os
from datetime import datetime, timedelta
from typing import Annotated, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.models.user import User, UserCRUD  # Update import path
from core.database import get_db

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from pydantic import BaseModel
# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await UserCRUD.get_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

def require_role(role: str):
    async def role_checker(
        user: Annotated[User, Depends(get_current_user)]
    ):
        if user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {role} role"
            )
        return user
    return role_checker

# Predefined role dependencies
AdminDep = Depends(require_role("admin"))
BuildingManagerDep = Depends(require_role("building_manager"))