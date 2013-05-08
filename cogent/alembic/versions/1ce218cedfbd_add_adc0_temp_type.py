"""add adc0 temp type

Revision ID: 1ce218cedfbd
Revises: 10d37b0cf10e
Create Date: 2013-05-08 14:42:37.679491

"""

# revision identifiers, used by Alembic.
revision = '1ce218cedfbd'
down_revision = '10d37b0cf10e'

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
                   [{'id': 6, 'name': "TempADC0 Node",
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
                   [{'id': 41, 'name': "Temperature ADC0",
                     'code': "T",
                     'units': "deg.C",
                     'c0': 0., 'c1': 1., 'c2': 0., 'c3': 0.},
                    {'id': 42, 'name': "Delta Temperature ADC0",
                     'code': "dT",
                     'units': "deg.C/s",
                     'c0': 0., 'c1': 1., 'c2': 0., 'c3': 0.}])

def downgrade():
    pass
