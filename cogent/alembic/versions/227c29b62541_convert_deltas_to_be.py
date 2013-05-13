"""convert deltas to be in seconds

Revision ID: 227c29b62541
Revises: 1ce218cedfbd
Create Date: 2013-05-13 11:30:19.101924

"""

# revision identifiers, used by Alembic.
revision = '227c29b62541'
down_revision = '1ce218cedfbd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from sqlalchemy.sql import table, column, text
from sqlalchemy import Integer, String, ForeignKey, DateTime, Float, Boolean, UniqueConstraint
import os,sys

if "TOSROOT" not in os.environ:
    raise Exception("Please source the Tiny OS environment script first")
sys.path.append(os.environ["TOSROOT"] + "/support/sdk/python")

from cogent.node import (AckMsg,
                         Packets)

deltas=[Packets.SC_D_TEMPERATURE,
        Packets.SC_D_HUMIDITY,
        Packets.SC_D_VOLTAGE,
        Packets.SC_D_AQ,
        Packets.SC_D_CO2,
        Packets.SC_D_VOC,
        Packets.SC_D_TEMPADC1]

deltas = ', '.join([str(x) for x in deltas]) 

def upgrade():
    op.execute('UPDATE Reading set Value=Value/300. WHERE type in ('+deltas+')');
    pass

def downgrade():
    op.execute('UPDATE Reading set Value=Value*300. WHERE type in ('+deltas+')');
    pass
