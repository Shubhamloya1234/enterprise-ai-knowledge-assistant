
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.tools.registry import register_tool
from app.models import Employee, Department
from app.models.user import User


@register_tool(
    "employee_search",
    "Search employees and retrieve employee information according to the authenticated user's access permissions."
)
def employee_search(
    db: Session,
    user_id: int,
    name: str | None = None,
    department: str | None = None
):
    # Retrieve the authenticated user from the database.
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User account no longer exists"
        )

    # Build the employee query.
    query = (
        db.query(Employee, Department)
        .join(
            Department,
            Employee.department_id == Department.id
        )
    )

    # ADMIN can search company-wide.
    if user.role == "ADMIN":
        pass

    # MANAGER can search only their linked department.
    elif user.role == "MANAGER":

        if user.employee_id is None or user.employee is None:
            raise HTTPException(
                status_code=403,
                detail="Your account is not linked to an employee record"
            )

        query = query.filter(
            Employee.department_id == user.employee.department_id
        )

    # EMPLOYEE can only retrieve their own record.
    elif user.role == "EMPLOYEE":

        if user.employee_id is None:
            raise HTTPException(
                status_code=403,
                detail="Your account is not linked to an employee record"
            )

        query = query.filter(
            Employee.id == user.employee_id
        )

    else:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions"
        )

    # Apply search filters after authorization.
    if name:
        query = query.filter(
            Employee.first_name.ilike(f"%{name}%")
            | Employee.last_name.ilike(f"%{name}%")
        )

    if department:
        query = query.filter(
            Department.name.ilike(f"%{department}%")
        )

    results = query.all()

    employees = []

    for employee, dept in results:
        employees.append({
            "id": employee.id,
            "name": f"{employee.first_name} {employee.last_name}",
            "email": employee.email,
            "job_title": employee.job_title,
            "department": dept.name
        })

    return {
        "count": len(employees),
        "employees": employees
    }
