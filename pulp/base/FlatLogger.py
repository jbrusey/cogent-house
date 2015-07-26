#
# FlatLogger
#
# log data from mote to a flat file and also print out
#
# J. Brusey, R. Wilkins, July 2015

"""FlatLogger - cogent-house data logging process.

Receives sensor readings from the base station and logs them to a flat file
This version also acknowledges logged data once it has been
successfully written to the file.

"""

import logging
import json
import sys
import os
import math
import time
from optparse import OptionParser
from pulp.node import (AckMsg,
                            Packets)
from pulp.base.SensorTypes import type_lookup
from BaseIF import BaseIF
from Queue import Empty
from datetime import datetime, timedelta
from packstate import PackState

LOGGER = logging.getLogger("pulp.base")
QUEUE_TIMEOUT = 10

def duplicate_packet():
    """ duplicate packets can occur because in a large network,
    the duplicate packet cache used is not sufficient. If such
    packets occur, then they will have the same node id, same
    local time and arrive within a few seconds of each other. In
    some cases, the first received copy may be corrupt and this is
    not dealt with within this code yet.
    """
    #To-Do assume no duplicate for now
    return False


class FlatLogger(object):
    """ FlatLogger class receives sensor messages and writes them to
    a flat file.
    """
    
    def __init__(self, bif=None):
        """ create a new FlatLogger and connect it to the sensor
        source (bif)
        """
        if bif is None: 
            self.bif = BaseIF("sf@localhost:9002")
        else:
            self.bif = bif

        self.time_count = 0.0 # how many seconds we've waited since last file
        self.last_time = time.time() # compare against for time_count
        self.log = logging.getLogger("flatlogger")
        self.running = True
        self.first=True
        self.out_fname = time.strftime("%Y_%j_%H-%M.log", time.gmtime())
        self.log_fname = '%s/%s'%(options.tmp_dir, self.out_fname)
        self.log.debug("Logging directory %s" % (self.log_fname))
        self.tmp_file = open(self.log_fname, 'w')
                             

    def send_ack(self,
                 seq=None,
                 dest=None):
        """ send acknowledgement message
        """
        ack_msg = AckMsg()
        ack_msg.set_seq(seq)
        ack_msg.set_node_id(dest)
        
        self.bif.sendMsg(ack_msg, dest)
        self.log.debug("Sending Ack %s to %s" %
                       (seq, dest))


    #To-Do not working
    def booted_node(self, msg):
        """Receieve and process a boot message object from the base station
        """

        # node_id = msg.getAddr()
        # clustered = msg.get_clustered()
        # version = msg.get_version()
        # version = "".join([chr(i) for i in version])
            
        # #To-Do: Decide where to store this
        # self.log.debug("boot: %s %s, %s, %s" % (current_time, node_id, clustered, version))

        return True


    def store_state(self, msg):
        """ receive and process a message object from the base station
        """
            
        # update amount of time we've been waiting
        tmp_time = time.time()
        self.time_count += tmp_time - self.last_time
        self.last_time = tmp_time

        # do we need to start a new file?
        if self.time_count >= float(options.duration):
            self.tmp_file.close()
                
            # move it
            try:
                os.rename(self.log_fname, "%s/%s"%(options.out_dir, self.out_fname))
            except OSError: # means that we're moving across partitions (IS THIS NEEDED?)
                os.system('mv %s %s/%s'%(self.log_fname, options.out_dir, self.out_fname))
            # ready for next interval
            self.time_count = 0
            # start new file
            self.out_fname = time.strftime("%Y_%j_%H-%M.log", time.gmtime())
            self.log_fname = '%s/%s'%(options.tmp_dir, self.out_fname)
            self.tmp_file = open(self.log_fname, 'w')

        if msg.get_special() != Packets.SPECIAL:
            raise Exception("Corrupted packet - special is %02x not %02x" %
                            (msg.get_special(), Packets.SPECIAL))
    
        pack_state = PackState.from_message(msg)

        output = {}
        for i, value in pack_state.d.iteritems():
            type_id = i
            if math.isinf(value) or math.isnan(value):
                value = None
            out_type = type_lookup[type_id]
            output[out_type] = value

 
        output['server_time'] = time.time()
        output['sender'] = msg.getAddr()
        output['parent'] = msg.get_ctp_parent_id()
        output['seq'] = msg.get_seq()
        output['rssi'] = msg.get_rssi()
        print output

        # prep output JSON line
        json_str = json.dumps(output) + "\n"

        # write to node file
        node_file = open('%s/node_%s.log'%(options.tmp_dir, output['sender']), 'w')
        node_file.write(json_str)
        node_file.close()

        graph_file = open('%s/node_%s_gnu.csv'%(options.out_dir, output['sender']), 'a')
        graph_file.write("%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%u,%u,%u\n"%(\
            output['server_time'], output['Temperature'], output['Humidity'],\
            output['ADC_0'], output['ADC_1'], output['ADC_2'], output['Voltage'],\
            output['parent'], output['rssi'], output['seq']))
        graph_file.close()
        
        # write to file in /tmp/
        self.tmp_file.write(json_str)
        self.tmp_file.flush()

        #send acknowledgement to base station to fwd to node
        self.send_ack(seq=output['seq'],
            dest=output['sender'])
                     
        return True

    def mainloop(self):
        """Break out run into a single 'mainloop' function

        Poll the bif.queue for data, if something has been received
        process and store.

        :return True: If a packet has been received and stored correctly
        :return False: Otherwise
        """
        try:
            msg = self.bif.queue.get(True, QUEUE_TIMEOUT)
            if msg.get_amType() == Packets.AM_BOOTMSG:
                #Log node boot
                status = self.booted_node(msg)
            elif msg.get_amType() == Packets.AM_STATEMSG:
                status = self.store_state(msg)
            else:
            	status = False
            #Signal the queue that we have finished processing
            self.bif.queue.task_done()
            return status
        except Empty:
            return False
        except KeyboardInterrupt:
            print "KEYB IRR"
            self.running = False
        except Exception as e:
            self.log.exception("during receiving or storing msg: " + str(e))


    def run(self):
        """ run - main loop

        At the moment this is just receiving from the sensor message
        queue and processing the message.

        """

        while self.running:
            self.mainloop()

                
if __name__ == '__main__': # pragma: no cover
    parser = OptionParser()
    
    parser.add_option("-o",
                        "--out-dir",
                        metavar="DIR",
                        default=".",
                        help="Output directory for files (default .)")
    parser.add_option("-t",
                        "--tmp-dir",
                        metavar="DIR",
                        default=".",
                        help="Temporary directory for files (default .)")
    parser.add_option("-d",
                        "--duration",
                        metavar="SEC",
                        default=900,
                        help="Number of seconds between files (default 900)")

    
    parser.add_option("-l", "--log-level",
                      help="Set log level to LEVEL: debug,info,warning,error",
                      default="info",
                      metavar="LEVEL")
    parser.add_option("-f", "--log-file",
                      help="Log file to use (Default ./Flatlogger.log",
                      default="/var/log/ch/FlatLogger.log")



    (options, args) = parser.parse_args()

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

    logging.info("Starting FlatLogger with log-level %s" % (options.log_level))
    lm = FlatLogger()
    lm.run()
