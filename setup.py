#from distutils.core import setup
from setuptools import setup
import os
import sys


REQUIRES = ['SQLAlchemy',
            "MySQL-python",
            'configobj',
            "python-dateutil==1.5",
            "python-rest-client",
            "numpy",
#            "matplotlib",
            "pyserial",
            "requests",
            "transaction",
            "python-daemon",
            "alembic",
#            "scipy",
            ]
    
setup(name='ch-base',
      version='1.1.3',
      description='CogentHouse base station logger',
      author='James Brusey, Ross Wilkins' 'Dan Goldsmith',
      author_email='james.brusey@gmail.com',
      packages=['cogent',
                'cogent.base',
                'cogent.base.model',
                'cogent.push',
                'cogent.report',
                'cogent.node',
                'cogent.scripts'],
      package_data={'cogent.base' : ['Calibration/*.csv']},
      data_files=[('/etc/init', ['etc/ch-sf.conf', 'etc/ch-base.conf', 'etc/noip2.conf']),
                  ('/etc/cron.daily', ['etc/ch-daily-email']),
                  ('/etc/apache2/sites-available', ['etc/cogent-house']),
                  ('/var/www/cogent-house', ['www/index.py']),
                  ('/var/www/scripts', ['www/scripts/datePicker.js']),
                  ('/var/www/style', ['www/style/ccarc.css']),
                  ("{0}/share/cogent-house/calibration".format(sys.prefix),["cogent/base/Calibration/aq_coeffs.csv",
                                                                            "cogent/base/Calibration/voc_coeffs.csv"]),
                  ],
      entry_points = """\
      [console_scripts]
      initialize_cogent_db = cogent.scripts.initializedb:main
      """,
      install_requires = REQUIRES,
      )
