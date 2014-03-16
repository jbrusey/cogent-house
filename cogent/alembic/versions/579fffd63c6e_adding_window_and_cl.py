"""Adding window and cluster CC type

Revision ID: 579fffd63c6e
Revises: 53bab55be06
Create Date: 2013-10-15 15:30:11.155825

"""

# revision identifiers, used by Alembic.
revision = '579fffd63c6e'
#down_revision = '53bab55be06'
down_revision = '162edc9b6f88'

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
                 [{'id': 8, 'name': "Window Sensor",
                   'time': "2011-07-10 00:00:00",
                   'seq': 1,
                   'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                  {'id': 12, 'name': "ClusterHead CC",
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
                 [{'id': 45, 'name': "Window State",
                   'code': "ste",
                   'units': "ste",
                   'c0': 0., 'c1': 1., 'c2': 0., 'c3': 0.}])

  
  op.bulk_insert(sensortype,
                 [{'id': 44, 'name': "Delta Opti",
                   'code': "imp",
                   'units': "imp",
                   'c0': 0., 'c1': 1., 'c2': 0., 'c3': 0.}])
  
  
def downgrade():
    pass
