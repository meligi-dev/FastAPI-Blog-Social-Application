from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    username:Mapped[str] = mapped_column(String,unique=True,index=True)
    email:Mapped[str] = mapped_column(String,unique=True,index=True)
    image_file:Mapped[str|None] = mapped_column(String(200),nullable=True,default=None)

    posts:Mapped[list[Post]] = relationship(back_populates="author", lazy="selectin")


    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"

class Post(Base):
    __tablename__ = "posts"
    id:Mapped[int] = mapped_column(Integer,primary_key=True,index=True)
    title:Mapped[str] = mapped_column(String,index=True)
    content:Mapped[str] = mapped_column(Text)
    date_posted:Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(UTC))
    user_id:Mapped[int] = mapped_column(Integer,ForeignKey("users.id"))
    
    author:Mapped[User] = relationship(back_populates="posts", lazy="selectin")