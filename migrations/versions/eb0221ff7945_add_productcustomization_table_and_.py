"""Add ProductCustomization table and relationships

Revision ID: eb0221ff7945
Revises: d42b47ca387e
Create Date: 2025-04-01 09:52:16.345967

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eb0221ff7945'
down_revision: Union[str, None] = 'd42b47ca387e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # Manually added table creation
    op.create_table('product_customizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('canvas_state', sa.JSON(), nullable=True),
        sa.Column('rendered_image_url', sa.String(length=512), nullable=False),
        sa.Column('selected_attributes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_product_customizations_id'), 'product_customizations', ['id'], unique=False)
    op.create_index(op.f('ix_product_customizations_product_id'), 'product_customizations', ['product_id'], unique=False)
    op.create_index(op.f('ix_product_customizations_user_id'), 'product_customizations', ['user_id'], unique=False)
    # End manually added table creation
    
    op.add_column('cart_items', sa.Column('product_customization_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_cart_items_product_customization_id_product_customizations'), 'cart_items', 'product_customizations', ['product_customization_id'], ['id'])
    op.drop_column('cart_items', 'customization')
    op.add_column('order_items', sa.Column('product_customization_id', sa.Integer(), nullable=True))
    op.create_foreign_key(op.f('fk_order_items_product_customization_id_product_customizations'), 'order_items', 'product_customizations', ['product_customization_id'], ['id'])
    op.drop_column('order_items', 'customization')
    op.add_column('products', sa.Column('sizes', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'sizes')
    op.add_column('order_items', sa.Column('customization', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_constraint(op.f('fk_order_items_product_customization_id_product_customizations'), 'order_items', type_='foreignkey')
    op.drop_column('order_items', 'product_customization_id')
    op.add_column('cart_items', sa.Column('customization', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_constraint(op.f('fk_cart_items_product_customization_id_product_customizations'), 'cart_items', type_='foreignkey')
    op.drop_column('cart_items', 'product_customization_id')
    
    # Manually added table drop
    op.drop_index(op.f('ix_product_customizations_user_id'), table_name='product_customizations')
    op.drop_index(op.f('ix_product_customizations_product_id'), table_name='product_customizations')
    op.drop_index(op.f('ix_product_customizations_id'), table_name='product_customizations')
    op.drop_table('product_customizations')
    # End manually added table drop
    # ### end Alembic commands ###
