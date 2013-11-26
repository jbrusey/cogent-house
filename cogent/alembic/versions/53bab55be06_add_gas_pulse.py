"""add gas pulse

Revision ID: 53bab55be06
Revises: 1ce218cedfbd
Create Date: 2013-05-30 11:26:41.102236

"""

# revision identifiers, used by Alembic.
revision = '53bab55be06'
down_revision = '1ce218cedfbd'

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
                   [{'id': 7, 'name': "Gas Node",
                     'time': "2011-07-10 00:00:00",
                     'seq': 1,
                     'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'}
                   ])
                   
    sensortype = table('SensorType',
                       column('id', Integer),
                       column('name', String(255)),
                       column('code', String(50)),
                       column('units', String(20)),
                       column('c0', Float),
                       column('c1', Float),
                       column('c2', Float),
                       column('c3', Float))
                       
    op.bulk_insert(sensortype,
                   [{'id': 43, 'name': "Gas Pulse Count",
                     'code': "imp",
                     'units': "imp",
                     'c0': 0., 'c1': 1., 'c2': 0., 'c3': 0.}])


def downgrade():
    pass
