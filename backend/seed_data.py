from app.db.database import SessionLocal
from app.models import Department, Employee, Task


db = SessionLocal()

try:
    # Departments
    engineering = Department(name="Engineering")
    sales = Department(name="Sales")
    human_resources = Department(name="Human Resources")

    db.add_all([
        engineering,
        sales,
        human_resources
    ])

    db.commit()

    # Employees
    employees = [
        Employee(
            first_name="Rahul",
            last_name="Sharma",
            email="rahul.sharma@company.com",
            job_title="Backend Developer",
            department_id=engineering.id
        ),
        Employee(
            first_name="Priya",
            last_name="Verma",
            email="priya.verma@company.com",
            job_title="Frontend Developer",
            department_id=engineering.id
        ),
        Employee(
            first_name="Amit",
            last_name="Kumar",
            email="amit.kumar@company.com",
            job_title="Sales Manager",
            department_id=sales.id
        ),
        Employee(
            first_name="Neha",
            last_name="Singh",
            email="neha.singh@company.com",
            job_title="Sales Executive",
            department_id=sales.id
        ),
        Employee(
            first_name="Anjali",
            last_name="Mehta",
            email="anjali.mehta@company.com",
            job_title="HR Manager",
            department_id=human_resources.id
        ),
        Employee(
            first_name="Rohan",
            last_name="Gupta",
            email="rohan.gupta@company.com",
            job_title="HR Executive",
            department_id=human_resources.id
        )
    ]

    db.add_all(employees)
    db.commit()

    # Tasks
    tasks = [
        Task(
            title="Build authentication API",
            description="Implement JWT authentication",
            status="IN_PROGRESS",
            priority="HIGH",
            employee_id=employees[0].id
        ),
        Task(
            title="Create employee dashboard",
            description="Build dashboard UI",
            status="COMPLETED",
            priority="HIGH",
            employee_id=employees[1].id
        ),
        Task(
            title="Optimize database queries",
            description="Improve API query performance",
            status="PENDING",
            priority="MEDIUM",
            employee_id=employees[0].id
        ),
        Task(
            title="Contact enterprise clients",
            description="Follow up with existing clients",
            status="IN_PROGRESS",
            priority="HIGH",
            employee_id=employees[2].id
        ),
        Task(
            title="Prepare sales report",
            description="Prepare monthly sales report",
            status="PENDING",
            priority="MEDIUM",
            employee_id=employees[3].id
        ),
        Task(
            title="Employee onboarding",
            description="Complete onboarding documentation",
            status="COMPLETED",
            priority="MEDIUM",
            employee_id=employees[4].id
        ),
        Task(
            title="Update company policies",
            description="Review HR policies",
            status="IN_PROGRESS",
            priority="LOW",
            employee_id=employees[4].id
        ),
        Task(
            title="Schedule employee interviews",
            description="Schedule upcoming interviews",
            status="PENDING",
            priority="HIGH",
            employee_id=employees[5].id
        )
    ]

    db.add_all(tasks)
    db.commit()

    print("Seed data inserted successfully!")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()