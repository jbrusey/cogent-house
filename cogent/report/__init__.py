"""Methods for reporting on status of cogent-house system"""

from cogent.report.lowbat import lowBat
from cogent.report.serverdown import server_down
from cogent.report.pantryhumid import pantry_humid
from cogent.report.fridgeopen import fridge_open
from cogent.report.packetyield import packetYield
from cogent.report.ccyield import ccYield

reports = [ 
    ('Nodes with low battery in last 24 hours', lowBat),
    ('Server down', server_down),
    ('Pantry damp', pantry_humid),
    ('Fridge open', fridge_open),
    #            ('Packet yield', packetYield),
    ('Current cost yield', ccYield),
]
