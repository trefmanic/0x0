"""Change File.addr to IPAddress type

Revision ID: d9a53a28ba54
Revises: 5cda1743b92d
Create Date: 2024-09-27 14:03:06.764764

"""

# revision identifiers, used by Alembic.
revision = 'd9a53a28ba54'
down_revision = '5cda1743b92d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import current_app
import ipaddress

Base = automap_base()


def upgrade():
    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('addr_tmp', sa.LargeBinary(16),
                                      nullable=True))

    bind = op.get_bind()
    Base.prepare(autoload_with=bind)
    File = Base.classes.file
    session = Session(bind=bind)

    updates = []
    stmt = sa.select(File).where(sa.not_(File.addr == None))
    for f in session.scalars(stmt.execution_options(yield_per=1000)):
        addr = ipaddress.ip_address(f.addr)
        if type(addr) is ipaddress.IPv6Address:
            addr = addr.ipv4_mapped or addr

        updates.append({
            "id": f.id,
            "addr_tmp": addr.packed
        })
    session.execute(sa.update(File), updates)

    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.drop_column('addr')
        batch_op.alter_column('addr_tmp', new_column_name='addr')


def downgrade():
    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.add_column(sa.Column('addr_tmp', sa.UnicodeText,
                                      nullable=True))

    bind = op.get_bind()
    Base.prepare(autoload_with=bind)
    File = Base.classes.file
    session = Session(bind=bind)

    updates = []
    stmt = sa.select(File).where(sa.not_(File.addr == None))
    for f in session.scalars(stmt.execution_options(yield_per=1000)):
        addr = ipaddress.ip_address(f.addr)
        if type(addr) is ipaddress.IPv6Address:
            addr = addr.ipv4_mapped or addr

        updates.append({
            "id": f.id,
            "addr_tmp": addr.compressed
        })

    session.execute(sa.update(File), updates)

    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.drop_column('addr')
        batch_op.alter_column('addr_tmp', new_column_name='addr')

