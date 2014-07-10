"""
Classes and Modules that represent house related objects

.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""


from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

import meta


class House(meta.Base, meta.InnoDBMix):
    """
    Class to represent Houses

    :var Integer id: Id of House

    :var Integer deploymentId: Id of parent
        :class:`cogentviewer.models.depoyment.Deployment`

    :var String address: Address of property
    :var DateTime startDate: start of deployment in this House
    :var endDate endDate: end of depoyment in this House

    :var meta: *backref*
        :class:`cogentviewer.models.housemetadata.HouseMetadata` objects
        belonging to this House

    :var occupiers: *backref*
        :class:`cogentviewer.models.occupier.Occupier` objects belonging
        to this house

    """
    __tablename__ = "House"

    id = Column(Integer, primary_key=True)
    deploymentId = Column(Integer, ForeignKey('Deployment.id'))
    address = Column(String(255))
    startDate = Column(DateTime)
    endDate = Column(DateTime)

    serverid = Column(Integer, ForeignKey("Server.id", use_alter=True, name="fk_house_server_id"), nullable=True)

    #Backrefs
    meta = relationship("HouseMetadata",
                        order_by="HouseMetadata.id",
                        backref="house")
    occupiers = relationship("Occupier", backref="house")
    locations = relationship("Location", backref="house")


    def __eq__(self, other):

        return (self.address == other.address and
                self.startDate == other.startDate and
                self.endDate == other.endDate)

    def __ne__(self, other):
        return not(self.address == other.address and
                   self.startDate == other.startDate and
                   self.endDate == other.endDate)

    def __lt__(self, other):
        if self.address == other.address:
            if self.startDate == other.startDate:
                return self.endDate < other.endDate
            return self.startDate < other.startDate
        return self.address < other.address


    def __str__(self):
        out = "House ({0}):  {1}  {2}-{3}".format(self.id,
                                                     self.address,
                                                     self.startDate,
                                                     self.endDate)
        return out
