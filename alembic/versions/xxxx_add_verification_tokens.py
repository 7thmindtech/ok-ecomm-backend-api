"""add verification tokens

Revision ID: xxxx
Revises: previous_revision_id
Create Date: 2024-xx-xx

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add verification_token and verification_token_expires columns
    op.add_column('users', sa.Column('verification_token', sa.String(255), nullable=True, unique=True))
    op.add_column('users', sa.Column('verification_token_expires', sa.DateTime(), nullable=True))

def downgrade():
    # Remove the columns if needed to rollback
    op.drop_column('users', 'verification_token_expires')
    op.drop_column('users', 'verification_token') 