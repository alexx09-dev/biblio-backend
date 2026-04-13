"""agregar es_favorito a libros

Revision ID: a1b2c3d4e5f6
Revises: 38ec04ad21c5
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '38ec04ad21c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'libros',
        sa.Column('es_favorito', sa.Boolean(), nullable=False, server_default='0')
    )


def downgrade() -> None:
    op.drop_column('libros', 'es_favorito')