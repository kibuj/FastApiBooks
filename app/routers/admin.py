from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.core.dependencies import RoleChecker
from app.models.models import User, UserRole

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.patch("/users/{user_id}/role", dependencies=[Depends(RoleChecker(["admin"]))])
def change_user_role(
        user_id: int,
        new_role: UserRole,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = new_role
    db.commit()
    return {"message": f"User role updated to {new_role.value}"}