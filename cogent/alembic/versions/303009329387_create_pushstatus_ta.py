"""Create PushStatus table

Revision ID: 303009329387
Revises: 4819f05fdf1c
Create Date: 2014-01-14 11:21:40.073987

"""

# revision identifiers, used by Alembic.
revision = '303009329387'
down_revision = '4819f05fdf1c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('Pushstatus',
                    sa.Column('id', sa.Integer, nullable=False),
                    sa.Column("time", sa.DateTime),
                    sa.Column("localtime", sa.DateTime),
                    sa.Column("hostname", sa.String(25)),
                    )

def downgrade():
    op.drop_table("Pushstatus")
    pass
