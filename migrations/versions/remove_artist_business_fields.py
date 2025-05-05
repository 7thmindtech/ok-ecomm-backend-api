"""remove_artist_business_fields

Revision ID: remove_artist_business_fields
Revises: 90563511b084
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Enum

# revision identifiers, used by Alembic.
revision: str = 'remove_artist_business_fields'
down_revision: Union[str, None] = '90563511b084'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Drop artist_id foreign key from products table
    op.drop_constraint('fk_products_artist_id_users', 'products', type_='foreignkey')
    
    # Drop artist_id column from products table
    op.drop_column('products', 'artist_id')
    
    # Drop artist and business related columns from users table
    op.drop_column('users', 'artist_bio')
    op.drop_column('users', 'artist_portfolio_url')
    op.drop_column('users', 'business_name')
    op.drop_column('users', 'business_registration_number')
    op.drop_column('users', 'business_address')
    
    # Update user_type enum to remove artist and business types
    op.execute("ALTER TYPE usertype RENAME TO usertype_old")
    op.execute("CREATE TYPE usertype AS ENUM('CUSTOMER', 'ADMIN')")
    op.execute((
        "ALTER TABLE users ALTER COLUMN user_type TYPE usertype USING "
        "CASE "
        "WHEN user_type::text = 'ARTIST' THEN 'CUSTOMER'::usertype "
        "WHEN user_type::text = 'BUSINESS' THEN 'CUSTOMER'::usertype "
        "ELSE user_type::text::usertype "
        "END"
    ))
    op.execute("DROP TYPE usertype_old")

def downgrade() -> None:
    # Recreate the old user_type enum
    op.execute("ALTER TYPE usertype RENAME TO usertype_old")
    op.execute("CREATE TYPE usertype AS ENUM('CUSTOMER', 'ARTIST', 'BUSINESS', 'ADMIN')")
    op.execute("ALTER TABLE users ALTER COLUMN user_type TYPE usertype USING user_type::text::usertype")
    op.execute("DROP TYPE usertype_old")
    
    # Add back artist and business related columns to users table
    op.add_column('users', sa.Column('artist_bio', sa.String(), nullable=True))
    op.add_column('users', sa.Column('artist_portfolio_url', sa.String(), nullable=True))
    op.add_column('users', sa.Column('business_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('business_registration_number', sa.String(), nullable=True))
    op.add_column('users', sa.Column('business_address', sa.String(), nullable=True))
    
    # Add back artist_id column to products table
    op.add_column('products', sa.Column('artist_id', sa.Integer(), nullable=True))
    
    # Add back artist_id foreign key to products table
    op.create_foreign_key(
        'fk_products_artist_id_users',
        'products', 'users',
        ['artist_id'], ['id']
    ) 