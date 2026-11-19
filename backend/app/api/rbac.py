from fastapi import APIRouter, Depends

from app.core.dependencies import require_role

router = APIRouter(
    prefix="/rbac",
    tags=["RBAC"]
)


@router.get("/admin")
def admin_only(
    current_user=Depends(require_role("ADMIN"))
):
    return {
        "message": "Welcome Admin",
        "role": current_user["role"]
    }


@router.get("/manager")
def manager_only(
    current_user=Depends(require_role("MANAGER"))
):
    return {
        "message": "Welcome Manager",
        "role": current_user["role"]
    }


@router.get("/employee")
def employee_only(
    current_user=Depends(require_role("EMPLOYEE"))
):
    return {
        "message": "Welcome Employee",
        "role": current_user["role"]
    }