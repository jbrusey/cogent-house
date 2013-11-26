"""make reading unique inc indexes

Revision ID: 10d37b0cf10e
Revises: 3a4338e38dea
Create Date: 2013-05-07 12:00:03.882279

"""

# revision identifiers, used by Alembic.
revision = '10d37b0cf10e'
down_revision = '3a4338e38dea'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from sqlalchemy.sql import table, column, text
from sqlalchemy import Integer, String, ForeignKey, DateTime, Float, Boolean, UniqueConstraint


def upgrade():
    op.create_index('ns_1', 'NodeState', ['time',
                                          'nodeId',
                                          'localtime'])
    
    op.create_index('r_1', 'Reading', ['time',
                                       'nodeId',
                                       'type'])

    op.create_index('nodeId_i', 'Reading', ['nodeId'])
    op.create_index('type_i', 'Reading', ['type'])
    op.create_index('locationId_i', 'Reading', ['locationId'])


    
def downgrade():
    op.drop_index('ns_1')
    op.drop_index('r_1')
    op.drop_index('nodeId_i')
    op.drop_index('type_i')
    op.drop_index('locationId_i')

