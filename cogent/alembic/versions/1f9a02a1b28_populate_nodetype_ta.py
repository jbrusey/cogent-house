"""populate nodetype table

Revision ID: 1f9a02a1b28
Revises: 25a5ee59d391
Create Date: 2013-01-16 10:19:56.860574

"""

# revision identifiers, used by Alembic.
revision = '1f9a02a1b28'
down_revision = '25a5ee59d391'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Float, DateTime



def upgrade():
    nodetype = table('NodeType',
                       column('id', Integer),
                       column('name', String(20)),
                       column('time', DateTime),
                       column('seq', Integer),
                       column('updated_seq', Integer),
                       column('period', Integer),
                       column('blink', Integer), #shouldbe tinyint
                       column('configured', String(10)))


    op.bulk_insert(nodetype,
                   [{'id': 0, 'name': "Base",
                     'time': "2011-07-10 00:00:00",
                     'seq': 1,
                     'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},

                   {'id': 1, 'name': "Current Cost",
                     'time': "2011-07-10 00:00:00",
                     'seq': 1,
                     'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,5'},

                   {'id': 2, 'name': "CO2",
                     'time': "2011-07-10 00:00:00",
                     'seq': 1,
                     'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '63,4'},

                   {'id': 3, 'name': "Air Quality",
                     'time': "2011-07-10 00:00:00",
                     'seq': 1,
                     'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '255,4'},
                   ])

    pass

def downgrade():
    pass
