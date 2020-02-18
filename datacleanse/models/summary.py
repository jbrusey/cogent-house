"""
Table to hold Summary Statistics

"""

import sqlalchemy
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
import meta
Base = meta.Base


# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref


class SummaryType(Base,meta.InnoDBMix):
    """
    Lookup table for Summary Types
    
    name:  Text based name of summary type (Ie Min, Average, count)
    code:  Short Text name or unit codes (ie Min,Avg)
    """
    __tablename__ = "SummaryType"
    
    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key=True)
    name= sqlalchemy.Column(sqlalchemy.String(30))
    code = sqlalchemy.Column(sqlalchemy.String(10))
                           
    

class Summary(Base,meta.InnoDBMix):
    """
    Table to hold summary statistics 
    This should allow uas to do any analysis a bit quicker than 
    looking through the tables and processing each datapoint.

    This is basically a extension of the reading table to allow 
    Sumamry information to be appended
    """
    
    __tablename__ = "Summary"
    time = sqlalchemy.Column(sqlalchemy.DateTime,
                             primary_key=True,
                             nullable=False,
                             autoincrement=False)

    nodeId = sqlalchemy.Column(sqlalchemy.Integer,
                               ForeignKey('Node.id'),
                               primary_key=True,
                               nullable=False,
                               autoincrement=False)

    sensorTypeId = sqlalchemy.Column(sqlalchemy.Integer, 
                                     ForeignKey('SensorType.id'),
                                     primary_key=True,
                                     nullable=True,
                                     autoincrement=False)

    summaryTypeId = sqlalchemy.Column(sqlalchemy.Integer,
                                      ForeignKey("SummaryType.id"),
                                      primary_key=True,
                                      nullable=False,
                                      autoincrement=False)

    locationId = sqlalchemy.Column(sqlalchemy.Integer,
                                   ForeignKey('Location.id'),
                                   primary_key = True,
                                   autoincrement=False)

    value = sqlalchemy.Column(Float)    

    textValue = sqlalchemy.Column(sqlalchemy.String(30))
                      
