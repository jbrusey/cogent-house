#from distutils.core import setup
from setuptools import setup
import os
import sys

#Fix for when a virtualenv is used to install
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here,"CHANGES.txt")).read()
CHANGES = open(os.path.join(here,"CHANGES.txt")).read()

#calcualte the prefix to instal data files into to meet debian FHS 
if sys.prefix  == "/usr":
    conf_prefix = "" #If its a standard "global" instalation
else :
    conf_prefix = "{0}/".format(sys.prefix)


REQUIRES = ['configobj',
            "python-dateutil==1.5",
            "numpy",
            "matplotlib",
            "pyserial",
            "requests",
            "transaction",
            ]
    
setup(name='ch-pulp',
      version='1.0.0',
      description='Cogent PULP base station logger',
      author='Ross Wilkins, James Brusey',
      author_email='ross.wilkins@coventry.ac.uk',
      packages=['pulp',
                'pulp.base',
                'pulp.sip',
                'pulp.node'
                ])
