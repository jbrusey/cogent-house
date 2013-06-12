"""Table to hold information on Timings"""

import sqlalchemy
import logging
LOG = logging.getLogger("Timings")
LOG.setLevel(logging.DEBUG)

import meta

import time

class Timings(meta.Base):
    __tablename__ = "Timings"
    
    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key = True)
    text = sqlalchemy.Column(sqlalchemy.Text,nullable=True)
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
    #print ("TIMED CALLED WITH FUNCTION ",function)

    def timeit(*args, **kwargs):

        session = meta.Session()
        #LOG.info("Timit Dectorator {0} {1}".format(args,kwargs))
        #log.debug("Timit Dectorator {0} {1}".format(args, kwargs))
        st = time.time()
        result = function(*args, **kwargs)
        et = time.time()
        total = et - st      
        theObj = Timings(function = str(function.__name__),
                         text = None,
                         args = str(args),
                         kwargs = str(kwargs),
                         time = total)
        
        session.add(theObj)

        session.flush()
        # #session.close()
        LOG.debug(theObj)
        return result
    return timeit


def timedtext(theText):
    """Decorator to log the amount of time taken by a function    
    This version allows a paramter (ie @timedtext("theText") to be inserted into the database
    """
    def wrap(function):  #Wrap the Outer Function and push the function into the namespace
        #print ("TIMED CALLED WITH FUNCTION ",function)
        def timeit(*args, **kwargs):
            session = meta.Session()
            #print ("Timit Dectorator {0} {1}".format(args, kwargs))
            st = time.time()
            result = function(*args, **kwargs)
            et = time.time()
            total = et - st
            theObj = Timings(function = str(function.__name__),
                             text = theText,
                             args = str(args),
                             kwargs = str(kwargs),
                             time = total)

            session.add(theObj)
            session.flush()
            # #session.close()
            LOG.debug(theObj)
            #LOG.info(theObj)
            return result

        return timeit
    return wrap

        #     # print "{} ({}, {}) = {}".format(function.__name__,
        #     #                                args,
        #     #                                kwargs,
        #     #                                total)
        #     theObj = Timings(function = str(function.__name__),
        #                      text = theText,
        #                      args = str(args),
        #                      kwargs = str(kwargs),
        #                      time = total)

        #     # session.add(theObj)
        #     # #session.flush()
        #     # #session.close()
        #     print theObj
        #     #LOG.info(theObj)
        #     return result
        # return timeit


