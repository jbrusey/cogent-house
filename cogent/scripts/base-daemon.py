"""
Daemonise the baselogger script.
Required for the RPI and sysvinit

:author:  Dan goldsmith <djgoldsmith@googlemail.com>
:version: 0.1
:date: October 2013
"""

#Python imports
import logging
import logging.handlers
import time
from daemon import *
from daemon import runner
import cogent.base.BaseLogger
import signal
import os

LOGFILE = "baselog.log"

#Subclass daemon.runner so that we can send a SIGINT to the baselogger
class DgRunner(runner.DaemonRunner):

    def _terminate_daemon_process(self):
        """ Terminate the daemon process specified in the current PID file.
        In my version we fist send a sigint (KeybaordInterrupt) to the process.
        This should allow the baselogger to shut down in a nice way.
        """

        pid = self.pidfile.read_pid()
        
        #DG - Rather than just kill the daemon process send a sigint
        os.kill(pid,signal.SIGINT)
        time.sleep(2) #Let it sleep for a couple of seconds to clean up.

        try:
            os.kill(pid, signal.SIGTERM)
        except OSError, exc:
            #DG- It may be the case that there is no such process (as we kiled it above)
            #In this case exit as a success
            if exc[0] == 3:
                log.debug("No Such Process, assuming the SIGINT worked")
                return 0
            raise runner.DaemonRunnerStopFailureError(
                u"Failed to terminate %(pid)d: %(exc)s" % vars())

#The app class that actually starts and stops the daemon
class App():
    def __init__(self):
        print "Initing App"
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/home/dang/cogent-house-Main/djgoldsmith-devel/cogent/tmp.pid'
        self.pidfile_timeout = 5
        self.detach_process = False
        self.runloop = True

        #Conditional start of the base program
#        if os.path.isfile(self.pidfile_path):
#            print "PID EXISTS"
#        else:
#            print "Starting Main"
#            self.lm = cogent.base.BaseLogger.BaseLogger()            
#
#        pass

    def run(self):
        #Main Code Goes here
        logging.debug("-----> Starting Main")
        #Check if we allready have a PID
        # if os.path.isfile(self.pidfile_path):
        #     logging.debug("Allready Running")
        #     return
        # else:
        #     print "Starting Main"
        #     lm = cogent.base.BaseLogger.BaseLogger()            
        #     lm.mainloop()


        lm = cogent.base.BaseLogger.BaseLogger()            
        lm.run()

        # while True:
        #     print "Looping"
        #     time.sleep(10)
           
        # lm.run()
        #lm.run()
        #time.sleep(2)
        logging.debug("Done")

#And boilerplate(ish) codez to register with python-deamon

if __name__ == "__main__":
    #Configure Logging
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = logging.handlers.RotatingFileHandler(LOGFILE,
                                                   maxBytes=1024*1024,
                                                   backupCount=3)
    #handler = logging.FileHandler(LOGFILE)

    handler.setFormatter(formatter)
    logging.getLogger('').addHandler(handler)
    logging.getLogger('').setLevel(logging.DEBUG)

    #And a debug one log for the console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    #And for the new version of daemon runner
    log = logging.getLogger('DG-Daemon')

    #Create an instance of the app
    app = App()
    #Create the daemon runner
    #daemonrunner = runner.DaemonRunner(app)
    daemonrunner = DgRunner(app)
    #This is important so the fid of the log doesnt get lost.
    daemonrunner.daemon_context.files_preserve =[handler.stream]

    #and handle start / stop / restart
    daemonrunner.do_action()

