import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DateTime, UniqueConstraint, Table
from app.core.database import Base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

class UserRole(str, enum.Enum):
    reader = "reader"
    writer = "writer"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.reader)
    is_active = Column(Boolean, default=True)

    books = relationship("Book", back_populates="author")
    votes = relationship("Vote", backref="user")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    author = relationship("User", back_populates="books")

    votes = relationship("Vote", backref="book")

    @property
    def likes_count(self):
        return len([v for v in self.votes if v.is_like is True])

    @property
    def dislikes_count(self):
        return len([v for v in self.votes if v.is_like is False])

    @property
    def rating(self):
        total_votes = self.likes_count + self.dislikes_count

        if total_votes == 0:
            return 0

        score = (self.likes_count / total_votes) * 10

        return round(score, 1)


class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id"), primary_key=True)

    is_like = Column(Boolean, nullable=False)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_id = Column(Integer, ForeignKey("users.id"))
    book_id = Column(Integer, ForeignKey("books.id"))

    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)   #посилання на батьківський коментар

    user = relationship("User", backref="comments")
    book = relationship("Book", backref="comments")

    replies = relationship(
        "Comment",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete"
    )  #відповіді на цей ж коментар і назад
