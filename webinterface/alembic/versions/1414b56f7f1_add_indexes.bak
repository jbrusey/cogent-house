"""add indexes

Revision ID: 1414b56f7f1
Revises: 1f9a02a1b28
Create Date: 2013-05-09 11:27:18.455059

"""

# revision identifiers, used by Alembic.
revision = '1414b56f7f1'
down_revision = '1f9a02a1b28'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_index('ns_1', 'NodeState', ['time',
                                          'nodeId',
                                          'localtime'])
    
    op.create_index('r_1', 'Reading', ['time',
                                       'nodeId',
                                       'type'])

    op.create_index('nodeId', 'Reading', ['nodeId'])
    op.create_index('type', 'Reading', ['type'])
    op.create_index('locationId', 'Reading', ['locationId'])

def downgrade():
    pass
