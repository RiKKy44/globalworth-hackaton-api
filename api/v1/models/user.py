from sqlalchemy import Column, Integer, String, Boolean  # Added Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from core.database import Base
from core.security import pwd_context  # Import pwd_context
from typing import Optional, Annotated
class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # Fixed Integer
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100))
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = "user"

    def create_db_user(self):
        return DBUser(
            email=self.email,
            hashed_password=pwd_context.hash(self.password),  # Use pwd_context
            full_name=self.full_name,
            role=self.role
        )

class User(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        orm_mode = True

class UserCRUD:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[DBUser]:
        result = await db.execute(select(DBUser).where(DBUser.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate):
        db_user = user.create_db_user()
        db.add(db_user)
        await db.commit()
        return db_user