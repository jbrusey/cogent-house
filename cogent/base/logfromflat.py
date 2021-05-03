#
# logfromflat
#
# Convert flat file containing JSON data into mysql reading records.
#
# Author: J. Brusey, November 2019
#
# Modification history:
#

"""LogFromFlat - convert json to mysql

"""

import logging
import math
import json
from optparse import OptionParser

from datetime import timedelta, datetime
from pathlib import Path

from cogent.base.model import (Reading,
                               NodeState,
                               SensorType,
                               Node)

import cogent.base.model as models
import cogent.base.model.meta as meta

from sqlalchemy import create_engine, and_
import sqlalchemy

LOGGER = logging.getLogger("ch.base")

DBFILE = "mysql://chuser@localhost/"
# DBFILE = "sqlite:///test.db"

PROCESSED_FILES = "processed_files.txt"


def duplicate_packet(session, receipt_time, node_id, localtime):
    """ duplicate packets can occur because in a large network,
    the duplicate packet cache used is not sufficient. If such
    packets occur, then they will have the same node id, same
    local time and arrive within a few seconds of each other. In
    some cases, the first received copy may be corrupt and this is
    not dealt with within this code yet.
    """
    assert isinstance(receipt_time, datetime)
    earliest = receipt_time - timedelta(minutes=1)
    return session.query(NodeState).filter(
        and_(NodeState.nodeId == node_id,
             NodeState.localtime == localtime,
             NodeState.time > earliest)).first() is not None


def add_node(session, node_id):
    """ add a database entry for a node
    """
    try:
        session.add(Node(id=node_id,
                         locationId=None,
                         nodeTypeId=(node_id / 4096)))
        session.commit()
    except Exception:
        session.rollback()
        LOGGER.exception("can't add node %d" % node_id)


class LogFromFlat(object):
    """ LogFromFlat class reads a JSON file and writes sensor readings to
    the database.
    """
    def __init__(self, dbfile=DBFILE):
        """ create a new LogFromFlat that reads from jsonfile and writes to dbfile
        """
        self.engine = create_engine(dbfile, echo=False)
        models.initialise_sql(self.engine)

        self.log = logging.getLogger("logfromflat")
        self.create_tables()

    def create_tables(self):
        """ create any missing tables using sqlalchemy
        """
        session = meta.Session()
        try:
            models.populateData.init_data(session)
            if session.query(SensorType).get(0) is None:
                raise Exception("SensorType must be populated by alembic before starting LogFromFlat")
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def store_state(self, msg):
        """ receive and process a message object from the base station
        """
        current_time = datetime.utcfromtimestamp(msg['server_time'])
        try:
            session = meta.Session()

            node_id = msg['sender']
            parent_id = msg['parent']
            seq = msg['seq']
            rssi_val = msg['rssi']

            node = session.query(Node).get(node_id)
            loc_id = None
            if node is None:
                add_node(session, node_id)
            else:
                loc_id = node.locationId

            if duplicate_packet(session=session,
                                receipt_time=datetime.utcfromtimestamp(msg['server_time']),
                                node_id=node_id,
                                localtime=msg['localtime']):
                LOGGER.info("duplicate packet %d->%d, %d %s" %
                            (node_id, parent_id, msg['localtime'], str(msg)))

                return False

            # write a node state row
            node_state = NodeState(time=datetime.utcfromtimestamp(msg['server_time']),
                                   nodeId=node_id,
                                   parent=parent_id,
                                   localtime=msg['localtime'],
                                   seq_num=seq,
                                   rssi=rssi_val)
            session.add(node_state)

            for i, value in list(msg.items()):
                # skip any non-numeric type_ids
                try:
                    type_id = int(i)
                except ValueError:
                    continue

                if math.isinf(value) or math.isnan(value):
                    value = None

                r = Reading(time=current_time,
                            nodeId=node_id,
                            typeId=type_id,
                            locationId=loc_id,
                            value=value)
                try:
                    session.add(r)
                    session.flush()

                except sqlalchemy.exc.IntegrityError as e:
                    self.log.error("Unable to store reading, checking if node type exists")
                    self.log.error(e)
                    session.rollback()
                    s = session.query(SensorType).filter_by(id=type_id).first()
                    if s is None:
                        s = SensorType(id=type_id, name="UNKNOWN")
                        session.add(s)
                        self.log.info("Adding new sensortype")
                        session.flush()
                        session.add(r)
                        session.flush()
                    else:
                        self.log.error("Sensor type exists")

            self.log.debug("reading: {}".format(node_state))
            session.commit()

        except Exception as exc:
            session.rollback()
            self.log.exception("error during storing (reading): " + str(exc))
            # don't continue if you get an error
            raise
        finally:
            session.close()

        return True

    def process_file(self, jsonfile):
        """ process a file from JSON into the database """
        with open(jsonfile, "r") as ff:
            for ll in ff:
                msg = json.loads(ll)
                self.store_state(msg)

    def process_dir(self, datadir):
        """process directory containing json log files into the database and
        update the log of files processed"""

        processed_set = set()

        pf = datadir / PROCESSED_FILES
        if pf.exists():
            with open(str(pf), 'r') as processed_files:

                for row in processed_files:
                    processed_set.add(row.rstrip())

        for logfile in datadir.glob('*.log'):
            if logfile.name not in processed_set and not logfile.is_dir():
                self.log.info("Processing {}".format(logfile))
                self.process_file(logfile)

            processed_set.add(logfile.name)

        def write_pf(pf, processed_set):
            with open(str(pf), 'w') as processed_files:
                for entry in processed_set:
                    processed_files.write(entry + '\n')

        try:
            write_pf(pf, processed_set)
        except PermissionError as e:
            self.log.exception(e)
            # try writing to the current directory instead

            mypf = Path.cwd() / PROCESSED_FILES
            write_pf(mypf, processed_set)
            self.log.info("Couldn't write to {}, so wrote {} instead".format(str(pf), str(mypf)))


if __name__ == '__main__':   # pragma: no cover
    parser = OptionParser()
    parser.add_option("-d", "--dir",
                      help="directory containing json files containing sensor readings",
                      default=None)

    parser.add_option("--database",
                      help="database to log to",
                      default=None)

    parser.add_option("-l", "--log-level",
                      help="Set log level to LEVEL: debug,info,warning,error",
                      default="debug",
                      metavar="LEVEL")

    parser.add_option("-f", "--log-file",
                      help="Log file to use (Default /var/log/ch/LogFromFlat.log",
                      default="/var/log/ch/LogFromFlat.log")

    parser.add_option("-t", "--log-terminal",
                      help="Echo Logging output to terminal",
                      action="store_true",
                      default=False)

    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("incorrect number of arguments")

    lvlmap = {"debug": logging.DEBUG,
              "info": logging.INFO,
              "warning": logging.WARNING,
              "error": logging.ERROR,
              "critical": logging.CRITICAL}

    if options.log_level not in lvlmap:
        parser.error("invalid LEVEL: " + options.log_level)

    logfile = options.log_file

    logging.basicConfig(filename=logfile,
                        filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s",
                        level=lvlmap[options.log_level])

    # And if we want to echo the output on the terminal
    logterm = options.log_terminal
    if logterm:
        console = logging.StreamHandler()
        console.setLevel(lvlmap[options.log_level])
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    if options.database is None:
        parser.error("--database must be specified")

    if options.dir is None:
        parser.error("--dir must be specified")

    logging.info("Starting LogFromFlat with log-level %s" % (options.log_level))
    lm = LogFromFlat(dbfile=DBFILE + options.database)
    lm.process_dir(Path(options.dir))
