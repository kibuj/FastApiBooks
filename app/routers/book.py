from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, RoleChecker
from app.core.email import send_notification_email
from app.models.models import Book, User, UserRole, Vote
from app.schemas import book as book_schema

router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


@router.get("/", response_model=List[book_schema.BookResponse])
def read_books(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        #current_user: User = Depends(get_current_user)  авторизація
):
    books = db.query(Book).offset(skip).limit(limit).all()
    return books


@router.post("/", response_model=book_schema.BookResponse, dependencies=[Depends(RoleChecker(["writer", "admin"]))])
def create_book(
        book: book_schema.BookCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    new_book = Book(
        title=book.title,
        description=book.description,
        author_id=current_user.id
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.put("/{book_id}", response_model=book_schema.BookResponse,
            dependencies=[Depends(RoleChecker(["writer", "admin"]))])
def update_book(
        book_id: int,
        book_update: book_schema.BookUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    #db_book = db.query(Book).filter(Book.id == book_id).first()
    db_book = db.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    if current_user.role != UserRole.admin and db_book.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this book")

    if book_update.title:
        db_book.title = book_update.title
    if book_update.description:
        db_book.description = book_update.description

    db.commit()
    db.refresh(db_book)
    return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["admin"]))])
def delete_book(
        book_id: int,
        db: Session = Depends(get_db)
):
    db_book = db.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()
    return None


@router.post("/{book_id}/vote", status_code=status.HTTP_200_OK)
def vote_book(
        book_id: int,
        is_like: bool,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    found_vote = db.query(Vote).filter(
        Vote.book_id == book_id,
        Vote.user_id == current_user.id
    ).first()

    if found_vote:
        if found_vote.is_like == is_like:
            db.delete(found_vote)
            message = "Vote removed"
        else:
            found_vote.is_like = is_like
            message = "Vote changed"
    else:
        new_vote = Vote(user_id=current_user.id, book_id=book_id, is_like=is_like)
        db.add(new_vote)
        message = "Voted successfully"

        if is_like:
            author_email = book.author.email if book.author else None

            if author_email:
                background_tasks.add_task(
                    send_notification_email,
                    email_to=[author_email],
                    subject="Someone liked your book!",
                    body=f"<h1>Hi!</h1><p>User {current_user.username} liked your book '{book.title}'.</p>"
                )

    db.commit()
    return {"message": message}
