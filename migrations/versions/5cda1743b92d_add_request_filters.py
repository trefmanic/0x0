"""Add request filters

Revision ID: 5cda1743b92d
Revises: dd0766afb7d2
Create Date: 2024-09-27 12:13:16.845981

"""

# revision identifiers, used by Alembic.
revision = '5cda1743b92d'
down_revision = 'dd0766afb7d2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import current_app
import ipaddress

Base = automap_base()


def upgrade():
    op.create_table('request_filter',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('type', sa.String(length=20), nullable=False),
                    sa.Column('comment', sa.UnicodeText(), nullable=True),
                    sa.Column('addr', sa.LargeBinary(length=16),
                              nullable=True),
                    sa.Column('net', sa.Text(), nullable=True),
                    sa.Column('regex', sa.UnicodeText(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('addr'))

    with op.batch_alter_table('request_filter', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_request_filter_type'), ['type'],
                              unique=False)

    bind = op.get_bind()
    Base.prepare(autoload_with=bind)
    RequestFilter = Base.classes.request_filter
    session = Session(bind=bind)

    blp = current_app.config.get("FHOST_UPLOAD_BLACKLIST")
    if blp:
        with current_app.open_instance_resource(blp, "r") as bl:
            for line in bl.readlines():
                if not line.startswith("#"):
                    line = line.strip()
                    if line.endswith(":"):
                        # old implementation uses str.startswith,
                        # which does not translate to networks
                        current_app.logger.warning(
                            f"Ignored address: {line}")
                        continue

                    addr = ipaddress.ip_address(line).packed
                    flt = RequestFilter(type="addr", addr=addr)
                    session.add(flt)

    for mime in current_app.config.get("FHOST_MIME_BLACKLIST", []):
        flt = RequestFilter(type="mime", regex=mime)
        session.add(flt)

    session.commit()

    w = "Entries in your host and MIME blacklists have been migrated to " \
        "request filters and stored in the databaes, where possible. " \
        "The corresponding files and config options may now be deleted. " \
        "Note that you may have to manually restore them if you wish to " \
        "revert this with a db downgrade operation."
    current_app.logger.warning(w)


def downgrade():
    with op.batch_alter_table('request_filter', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_request_filter_type'))

    op.drop_table('request_filter')
