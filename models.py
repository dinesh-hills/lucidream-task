from typing import List
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=100), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(length=100), nullable=False)

    posts: Mapped[List["Post"]] = relationship(
        back_populates="user",
    )

    @classmethod
    def get_user_or_none(cls, session: Session, email):
        return session.query(cls).where(cls.email == email).one_or_none()

    def fetch_posts(self, session: Session) -> List["Post"]:
        return session.query(Post).filter(Post.user_id == self.id).all()

    def __repr__(self):
        return f"<User(email='{self.email}', password='{self.password}')>"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text)

    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="posts")
