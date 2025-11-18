from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.models import Comment, Book, User
from app.schemas import comment as comment_schema

router = APIRouter(tags=["Comments"])


@router.post("/books/{book_id}/comments", response_model=comment_schema.CommentResponse)
def create_comment(
        book_id: int,
        comment_data: comment_schema.CommentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if comment_data.parent_id:
        parent = db.query(Comment).filter(Comment.id == comment_data.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        # Перевірка, щоб не відповідали на коментар з іншої книги (захист)
        if parent.book_id != book_id:
            raise HTTPException(status_code=400, detail="Parent comment belongs to another book")

    new_comment = Comment(
        text=comment_data.text,
        user_id=current_user.id,
        book_id=book_id,
        parent_id=comment_data.parent_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.get("/books/{book_id}/comments", response_model=List[comment_schema.CommentResponse])
def get_comments(
        book_id: int,
        db: Session = Depends(get_db)
):
    # підтягне вкладені коментарі у поле replies.
    comments = db.query(Comment).filter(
        Comment.book_id == book_id,
        Comment.parent_id == None
    ).all()

    return comments

#FastAPI бере список кореневих коментарів.
#Починає перетворювати перший коментар у JSON.
#Бачить у схемі поле "replies".
#Іде в модель SQLAlchemy -> relationship "replies".
#SQLAlchemy автоматично робить запит до БД: "Дай дітей цього коментаря".
#Pydantic записує їх у список.
#Якщо у дітей є свої діти — процес повторюється (рекурсія).