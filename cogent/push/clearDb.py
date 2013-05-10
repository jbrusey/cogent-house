"""
Utility Function to remove all data from a given DB
"""

#DBURL = ['mysql://test_user:test_user@localhost/pushTest',
#         'mysql://test_user:test_user@localhost/pushSource']

DBURL = ['mysql://dang:j4a77aec@127.0.0.1:3307/chtest']

#DBURL = ['mysql://test_user:test_user@localhost/pushTest']


import sqlalchemy
import cogent.base.model as models
import cogent.base.model.meta as meta

for url in DBURL:
    engine = sqlalchemy.create_engine(url)

    models.initialise_sql(engine,True)
    models.populate_data()
