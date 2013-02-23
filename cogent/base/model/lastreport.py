import sqlalchemy
import logging
log = logging.getLogger(__name__)

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean

import meta
Base = meta.Base

class LastReport(Base,meta.InnoDBMix):
    """
    Class to deal with LastReports
	This holds details of the last report E-Mailed to chuser

    :var String name: Name 
    :var String value: Value 

    """

    __tablename__ = "LastReport"

    name = Column(String(40), primary_key=True)
    value = Column(String(4096))
