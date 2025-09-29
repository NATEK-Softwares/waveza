"""Add push_subscription to user table

Revision ID: bea2387572ce
Revises: 3481c85ebb7b
Create Date: 2025-09-29 18:43:20.196259

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bea2387572ce'
down_revision = '3481c85ebb7b'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user', sa.Column('push_subscription', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('user', 'push_subscription')
