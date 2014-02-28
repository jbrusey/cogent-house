"""
Methods to time how long functions take to run

Consists of a decorator function that can be applied to preixisting code
this will check the running time of that function call and insert a record
into the database

:author: Daniel goldsmith <djgoldsmith@googlemail.com>
"""

import sqlalchemy
import logging
LOG = logging.getLogger("Timings")
LOG.setLevel(logging.DEBUG)

import meta

import time

class Timings(meta.Base):
    """Table to hold the timing information"""
    __tablename__ = "Timings"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key = True)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    function = sqlalchemy.Column(sqlalchemy.Text)
    args = sqlalchemy.Column(sqlalchemy.Text)
    kwargs = sqlalchemy.Column(sqlalchemy.Text)
    time = sqlalchemy.Column(sqlalchemy.Float)

    def __str__(self):
        return "[{0}] {5} {1} ({2}, {3}) = {4}s".format(self.id,
                                                        self.function,
                                                        self.args,
                                                        self.kwargs,
                                                        self.time,
                                                        self.text)



def timed(function):
    """Decorator to log the amount of time taken by a function
    """

    def timeit(*args, **kwargs):
        session = meta.Session()
        starttime = time.time()
        result = function(*args, **kwargs)
        endtime = time.time()
        total = endtime - starttime
        timeobject = Timings(function = str(function.__name__),
                             text = None,
                             args = str(args),
                             kwargs = str(kwargs),
                             time = total)

        session.add(timeobject)

        session.flush()
        # #session.close()
        LOG.debug(timeobject)
        return result
    return timeit


def timedtext(theText):
    """Decorator to log the amount of time taken by a function
    This version allows a paramter (ie @timedtext("theText")
    to be inserted into the database
    """
    def wrap(function):
        #Wrap the Outer Function and push the function into the namespace

        def timeit(*args, **kwargs):
            session = meta.Session()
            starttime = time.time()
            result = function(*args, **kwargs)
            endtime = time.time()
            total = endtime - starttime
            timeobject = Timings(function = str(function.__name__),
                             text = theText,
                             args = str(args),
                             kwargs = str(kwargs),
                             time = total)

            session.add(timeobject)
            session.flush()
            # #session.close()
            LOG.debug(timeobject)
            #LOG.info(timeobject)
            return result

        return timeit
    return wrap
