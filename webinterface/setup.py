import os
import sys

from setuptools import setup, find_packages
#from distutils import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

#calcualte the prefix to instal data files into to meet debian FHS 
if sys.prefix  == "/usr":
    conf_prefix = "" #If its a standard "global" instalation
else:
    conf_prefix = "{0}/".format(sys.prefix)


requires = [
    'pyramid==1.3.4',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    "python-dateutil==1.5",
    'MySQL-python',
    "WebTest",
    "pyrrd",
    "passlib",
    "demjson", #Until RRD 1.4.8 comes out
    "requests",
    "pandas>=0.12.0", #Maths Munging
    "alembic",
    "nose", #For testing
    "coverage", #For Testing
    ]


setup(name='cogent-viewer',
      version='0.4.4',
      description='cogent-viewer',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Daniel Goldsmith',
      author_email='djgoldsmith@googlemail.com',
      url='https://launchpad.net/cogent-house',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='cogentviewer',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = cogentviewer:main
      [console_scripts]
      initialize_webinterface_db = cogentviewer.scripts.initializedb:main
      initialize_testing_db = cogentviewer.scripts.init_testingdb:main
      add_webinterface_user = cogentviewer.scripts.addUser:main
      get_webinterface_js = cogentviewer.scripts.getjs:main
      """,
      #package_data={'cogentviewer':['calibration/*.csv']},
      data_files = [("{0}/share/cogent-house/calibration".format(sys.prefix),["calibration/aq_coeffs.csv",
                                                                              "calibration/co2_coeffs.csv",
                                                                              "calibration/hum_coeffs.csv",
                                                                              "calibration/temp_coeffs.csv",
                                                                              "calibration/voc_coeffs.csv"]),
                    #("{0}/share/cogent-house/alembic".format(sys.prefix),["
                    ],
      )

