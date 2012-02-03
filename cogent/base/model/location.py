from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship, backref

from cogent.base.model.meta import Base

Location = sqlalchemy.Table('Location',Base.metadata,
                            Column("id",Integer,primary_key=True),
                            Column("houseId",Integer,ForeignKey('House.id')),
                            Column("roomId",Integer,ForeignKey('Room.id'))
                            )        
        
