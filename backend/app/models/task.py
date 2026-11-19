from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(200), nullable=False)
    description = Column(String(500))

    status = Column(String(50), nullable=False, default="PENDING")
    priority = Column(String(50), nullable=False, default="MEDIUM")

    employee_id = Column(
        Integer,
        ForeignKey("employees.id"),
        nullable=False
    )

    employee = relationship(
        "Employee",
        back_populates="tasks"
    )