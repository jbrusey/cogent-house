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


REQUIRES = ['SQLAlchemy',
            "MySQL-python",
            'configobj',
            "python-dateutil==1.5",
            "numpy",
            "matplotlib",
            "pyserial",
            "requests",
            "transaction",
            "alembic",
            ]
    
setup(name='ch-base',
      version='1.1.6',
      description='CogentHouse base station logger',
      author='James Brusey, Ross Wilkins Dan Goldsmith',
      author_email='james.brusey@gmail.com',
      packages=['cogent',
                'cogent.base',
                'cogent.base.model',
                'cogent.push',
                'cogent.report',
                'cogent.sip',
                'cogent.node',
		'cogent.scripts'
                ],
      include_package_data=True,
      data_files=[('{0}/etc/init.d'.format(conf_prefix), ["etc/ch-base", "etc/ch-sf"]),
                  ('{0}/etc/cron.daily'.format(conf_prefix), ['etc/ch-daily-email']),
                  ('{0}/etc/apache2/sites-available'.format(conf_prefix), ['etc/cogent-house']),
                  ('{0}/var/www/cogent-house'.format(conf_prefix), ['www/index.py']),
                  ('{0}/var/www/scripts'.format(conf_prefix), ['www/scripts/datePicker.js']),
                  ('{0}/var/www/style'.format(conf_prefix), ['www/style/ccarc.css']),
                  #Push Configuration Files
                  ("{0}/etc/cogent-house/push-script/".format(conf_prefix),["conf/push-script/synchronise.template"])
                  ],
      entry_points = """\
      [console_scripts]
      initialize_cogent_db = cogent.scripts.initializedb:main
      """,
      install_requires = REQUIRES,
      )
