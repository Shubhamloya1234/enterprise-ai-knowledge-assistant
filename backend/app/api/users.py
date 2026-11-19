from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User
from app.core.dependencies import require_role
from app.core.security import hash_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/")
def create_user(
    username: str,
    email: str,
    password: str,
    role: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("ADMIN"))
):
    if role not in ["ADMIN", "MANAGER", "EMPLOYEE"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    existing_user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User created successfully",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }


@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("ADMIN"))
):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]