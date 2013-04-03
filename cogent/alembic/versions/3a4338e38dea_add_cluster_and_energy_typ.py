"""add cluster head type to nodestate

Revision ID: 3a4338e38dea
Revises: 2e63cc74b5ad
Create Date: 2013-02-28 15:27:39.736026

"""

# revision identifiers, used by Alembic.
revision = '3a4338e38dea'
down_revision = '2e63cc74b5ad'

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
                   [{'id': 10, 'name': "ClusterHead CO2",
                     'time': "2011-07-10 00:00:00",
                     'seq': 1,
                     'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                     {'id': 11, 'name': "ClusterHead AQ",
                     'time': "2011-07-10 00:00:00",
                     'seq': 1,
                     'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'},
                    {'id': 5, 'name': "EnergyBoard",
                     'time': "2011-07-10 00:00:00",
                     'seq': 1,
                     'updated_seq': 0., 'period': 307200., 'blink': 0., 'configured': '31,4'}
                   ])
    pass

def downgrade():
    pass
