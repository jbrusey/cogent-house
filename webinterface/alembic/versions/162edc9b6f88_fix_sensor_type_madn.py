"""Fix Sensor Type Madness

This fixes several problems that are present due to the
Alemic reviesion 25a5ee59d391_populate_sensor_type being modified.
This means that we can have versions of the DB that are the same (according to alembic), but have differing content / sensorTypeId's depending on when the revision was applied.

Revision ID: 162edc9b6f88
Revises: 53bab55be06
Create Date: 2013-10-09 14:00:06.502954

"""

"""
This doesn't appear to be a problem in the standard version, however clustered has had seveal changes committed

Additionaly, later alembic revisions then add sensor types that are missing / ids have been changed 

(Revision 1ce218cedfbd) 
Adds / Brings back

* Temperature ADC0 (Id 41)
* Delta Temperture ADC0 (Id 42)

(Revision 53bab55be06)

* Gas Pulses

I strugle a little to think of a sane way to fix this.  Only thing that springs
to mind (that doesn't involve manually looking at a load of records, or haing
the bulk insert statment bork) is to:

1) Update all sensor types via the Initialise DB script
2) Run an alembic script that makes sure that all data with a given Id, references the new id.


I would also argue against adding new sensor types via alembic. 

"""

# revision identifiers, used by Alembic.
revision = '162edc9b6f88'
down_revision = '53bab55be06'

from alembic import op
import sqlalchemy as sa

##Reading Table
reading = sa.sql.table('Reading',
                       sa.sql.column('type',sa.Integer)
                       )

def upgrade():
    #These have been Renumbered between revisions

    print "WARNING:: THIS EXPECTS THE CORRECT SENSOR TYPES TO BE IN THE READING TABLE"
    print "USE THE initialise_webinterface_db SCRIPT TO ACHIEVE THIS"

    #20 was Electricity Pulse -> Delta CO2 (Elec Becomes  ID 40)
    #21 was Temp ADC1 -> Delta VOC  (ADC1 Becoms 41)
    #22 was Temp ADC2 -> Delta AQ   (Need Sensor Type)
    #23 was Black Bulb -> Temperature Health (No Sensor)
    #24 was Gas Pulse -> Temperature Cold  (Becomes type 43)

    #New Sensor Types
    op.execute(
        reading.update().where(reading.c.type==op.inline_literal(20)).values({'type':op.inline_literal(40)})
        )
    op.execute(
        reading.update().where(reading.c.type==op.inline_literal(21)).values({'type':op.inline_literal(41)})
        )
    op.execute(
        reading.update().where(reading.c.type==op.inline_literal(24)).values({'type':op.inline_literal(43)})
        )

    pass


def downgrade():
    pass
