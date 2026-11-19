
"""add_sources_to_messages

Revision ID: e82a91c4b7d0
Revises: d65dc8ccf67e
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e82a91c4b7d0"
down_revision: Union[str, Sequence[str], None] = "d65dc8ccf67e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column("sources", sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("messages", "sources")
