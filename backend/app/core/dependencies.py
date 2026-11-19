from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        return payload

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


def get_current_user_record(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.id == current_user["user_id"]
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User account no longer exists"
        )

    return user


def require_role(required_role: str):

    def role_checker(
        user: User = Depends(get_current_user_record)
    ):
        if user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )

        return {
            "user_id": user.id,
            "role": user.role,
            "employee_id": user.employee_id
        }

    return role_checker


def require_linked_employee(
    user: User = Depends(get_current_user_record)
):
    if user.employee_id is None or user.employee is None:
        raise HTTPException(
            status_code=403,
            detail="Your account is not linked to an employee record"
        )

    return user