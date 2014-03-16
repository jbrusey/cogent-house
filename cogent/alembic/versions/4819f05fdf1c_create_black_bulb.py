"""Create Black Bulb

Revision ID: 4819f05fdf1c
Revises: fb241d5c070
Create Date: 2014-01-10 10:57:45.212496

"""

# revision identifiers, used by Alembic.
revision = '4819f05fdf1c'
down_revision = 'fb241d5c070'

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

    sensortype = table('SensorType',
                       column('id', Integer),
                       column('name', String(255)),
                       column('code', String(50)),
                       column('units', String(20)),
                       column('c0', Float),
                       column('c1', Float),
                       column('c2', Float),
                       column('c3', Float))


    op.bulk_insert(nodetype,
                   [{'id': 13, 
                     'name': "ClusterHead BB",
                     'time': "2011-07-10 00:00:00",
                     'seq': 1,
                     'updated_seq': 0., 
                     'period': 307200., 
                     'blink': 0., 
                     'configured': '31,4'},
                    ])

    op.bulk_insert(sensortype,
                   [{'id' : 46,
                     'name' : "Black Bulb",
                     'code' : "bb",
                     'units' : "v",
                     'c0' : 0.,
                     'c1' : 0.,
                     'c2' : 0.,
                     'c3' : 0.,
                    },
                    {'id' : 47,
                     'name' : "Delta Black Bulb",
                     'code' : "d/bb",
                     'units' : "v/s",
                     'c0' : 0.,
                     'c1' : 0.,
                     'c2' : 0.,
                     'c3' : 0.,
                     }
                    ])

def downgrade():
    pass
