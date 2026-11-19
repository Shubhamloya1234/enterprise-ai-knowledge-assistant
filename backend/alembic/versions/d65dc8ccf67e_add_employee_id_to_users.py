"""add_employee_id_to_users

Revision ID: d65dc8ccf67e
Revises: 1fe2b08de3a3
"""

from typing import Sequence, Union  # noqa: I001, UP035

from alembic import op  # ty: ignore[unresolved-import]
import sqlalchemy as sa


revision: str = "d65dc8ccf67e"
down_revision: Union[str, Sequence[str], None] = "1fe2b08de3a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("employee_id", sa.Integer(), nullable=True),
    )

    op.create_unique_constraint(
        "uq_users_employee_id",
        "users",
        ["employee_id"],
    )

    op.create_foreign_key(
        "fk_users_employee_id_employees",
        "users",
        "employees",
        ["employee_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_users_employee_id_employees",
        "users",
        type_="foreignkey",
    )

    op.drop_constraint(
        "uq_users_employee_id",
        "users",
        type_="unique",
    )

    op.drop_column("users", "employee_id")