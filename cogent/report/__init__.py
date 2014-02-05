"""Methods for reporting on status of cogent-house system"""

from cogent.report.lowbat import lowBat
from cogent.report.packetyield import packetYield
from cogent.report.ccyield import ccYield

reports = [ 
            ('Nodes with low battery in last 24 hours', lowBat),
            ('Packet yield', packetYield),
            ('Current cost yield', ccYield),
           ]
