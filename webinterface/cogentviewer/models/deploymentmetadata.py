"""
.. codeauthor::  Ross Wiklins
.. codeauthor::  James Brusey
.. codeauthor::  Daniel Goldsmith <djgoldsmith@googlemail.com>
"""

#SQL Alchemy Relevant information
from sqlalchemy import Column, Integer, String, ForeignKey, Float

#And Backrefs and Relations.

#Import Pyramid Meta Data
import meta

class DeploymentMetadata(meta.Base, meta.InnoDBMix):
    """
    Table to hold metadata about a deployment

    :var integer id:
    :var integer deploymentId: *Foreign key* to `Deployment`
    :var string name:  Name of metadata
    :var string description: Description of metadata
    :var string units: Units of metadata
    :var float value: Value of metadata
    """

    __tablename__ = "DeploymentMetadata"

    id = Column(Integer, primary_key=True)
    deploymentId = Column(Integer, ForeignKey('Deployment.id'))
    name = Column(String(255))
    description = Column(String(255))
    units = Column(String(255))
    value = Column(Float)

    def __str__(self):
        return "Meta {0}: {1}".format(self.id, self.deploymentId)
