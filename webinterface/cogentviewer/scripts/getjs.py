import os
import sys
#import requests
import os
import os.path
import urllib
import tarfile
import shutil

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)


def main(argv=sys.argv):
    print "Downloading"

    thePath = os.path.relpath(os.path.join("cogentviewer","jslibs"))
   
    #Create a JS directory if it doesnt exits
    if not os.path.exists(thePath):
        print "Exists {0}".format(os.path.exists(thePath))
        os.makedirs(thePath)

    DOJO_URL = "http://download.dojotoolkit.org/release-1.8.3/dojo-release-1.8.3.tar.gz"

    print "Downloading Dojo"
    dojoFile =os.path.join(thePath,"dojo.tar.gz")
    if os.path.exists(dojoFile):
        print "Dojo Exists"        
    else:
        print "Downloading Dojo"
        urllib.urlretrieve(DOJO_URL,dojoFile)
        dojoTar = tarfile.open(dojoFile)
        dojoTar.extractall(thePath)
        shutil.move(os.path.join(thePath,"dojo-release-1.8.3"),os.path.join(thePath,"dojo"))    




    #if len(argv) != 2:
    #    usage(argv)
    #config_uri = argv[1]
    #setup_logging(config_uri)
    #settings = get_appsettings(config_uri)
