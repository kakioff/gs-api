"""update user role

Revision ID: 178c07571429
Revises: 21f71e1435d5
Create Date: 2024-06-16 16:47:30.563171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '178c07571429'
down_revision: Union[str, None] = '21f71e1435d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'role_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'role_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
