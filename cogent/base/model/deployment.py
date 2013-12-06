"""
Table to represent deployments.

.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""


#SQL Alchemy Relevant information
from sqlalchemy import Column, Integer, String, DateTime

#And Backrefs and Relations.
from sqlalchemy.orm import relationship

#Import Pyramid Meta Data
import meta

class Deployment(meta.Base, meta.InnoDBMix):
    """Table to hold information about deployments.

    :var integer id: deployment id (pk)
    :var string name: deployment name
    :var string description: deployment description
    :var DateTime startDate: deployment start date
    :var DateTime endDate: deployment end date

    :var list meta: *Backref:* all
        :class:`cogentviewer.models.housemetadata.HouseMetadata` linked to this
        deployment

    :var list houses: *Backref:* all
        :class:`cogentviewer.models.house.House` objects in this deployment
    """

    __tablename__ = "Deployment"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))
    startDate = Column(DateTime)
    endDate = Column(DateTime)

    meta = relationship("DeploymentMetadata",
                        order_by="DeploymentMetadata.id",
                        backref="deployment")
    houses = relationship("House", order_by="House.id", backref="deployment")


    def __str__(self):
        return "Deployment: {0} {1} {2} - {3}".format(self.id,
                                                      self.name,
                                                      self.startDate,
                                                      self.endDate)


    def __eq__(self, other):
        """Check for equality

        Given that Deployment Names should be Unique,
        equality is given if the names match
        """
        return self.name == other.name
        #return (self.id == other.id) and (self.name == other.name)


    def __ne__(self, other):
        """Check for Inequality"""
        return not(self.name == other.name)
        #return not(self.id == other.id and self.name == other.name)

    def __lt__(self, other):
        """Order Objects,
        """
        #if self.id == other.id:
        return self.name < other.name

        #if self.id < other.id:
        #    if self.name == other.name:
        #        return True
        #    else:
        #        return self.name < other.name
        #return False
