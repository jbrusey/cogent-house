import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

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
    ]


setup(name='cogent-viewer',
      version='0.2',
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
      url='',
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
      """,
      )

