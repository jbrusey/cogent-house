"""Move all tables to InnoDB

(This Does skip some tables,  We will Proberbly end up removing these in the very need future)

Revision ID: 249f360e32e3
Revises: 406589edcb82
Create Date: 2012-06-06 12:57:50.392285

"""

# revision identifiers, used by Alembic.
revision = '249f360e32e3'
down_revision = '406589edcb82'

from alembic import op
import sqlalchemy as sa

from sqlalchemy.sql import table, column, text

def upgrade():
    op.execute(text('ALTER TABLE Deployment ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE House ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE Location ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE Node ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE NodeHistory ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE NodeState ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE NodeType ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE Reading ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE Room ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE RoomType ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE Sensor ENGINE = INNODB;'))    
    op.execute(text('ALTER TABLE SensorType ENGINE = INNODB;'))    
    pass


def downgrade():
    pass
