"""Create categories table

Revision ID: 20240320_create_categories
Revises: 
Create Date: 2024-03-20 13:46:03.429508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20240320_create_categories'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('category',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['parent_id'], ['category.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_category_id'), 'category', ['id'], unique=False)

    # Add category_id to products table
    op.add_column('products', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'products', 'category', ['category_id'], ['id'])

    # Seed initial categories
    op.execute("""
    INSERT INTO category (name, description, slug, is_active, created_at, updated_at)
    VALUES 
        ('Paintings', 'Beautiful paintings by various artists', 'paintings', true, now(), now()),
        ('Sculptures', 'Hand-crafted sculptures in various materials', 'sculptures', true, now(), now()),
        ('Digital Art', 'Modern art created using digital tools', 'digital-art', true, now(), now()),
        ('Photography', 'Professional photography prints', 'photography', true, now(), now()),
        ('Jewelry', 'Handmade jewelry and accessories', 'jewelry', true, now(), now())
    """)


def downgrade():
    # Remove foreign key and column from products
    op.drop_constraint(None, 'products', type_='foreignkey')
    op.drop_column('products', 'category_id')
    
    # Drop the category table
    op.drop_index(op.f('ix_category_id'), table_name='category')
    op.drop_table('category') 