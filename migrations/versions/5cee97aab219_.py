"""add date of last virus scan

Revision ID: 5cee97aab219
Revises: e2e816056589
Create Date: 2022-12-10 16:39:56.388259

"""

# revision identifiers, used by Alembic.
revision = '5cee97aab219'
down_revision = 'e2e816056589'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('file', sa.Column('last_vscan', sa.DateTime(),
                                    nullable=True))


def downgrade():
    op.drop_column('file', 'last_vscan')
