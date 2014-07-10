#! /bin/python

import os
import sys
#import requests
import os
import os.path
import urllib
import tarfile
import zipfile
import shutil
import subprocess

DOJO_VERSION = "1.9.0"
HIGHCHARTS_VERSION = "3.0.5"
HIGHSTOCK_VERSION = "1.3.5"
JQUERY_VERSION = "1.10.1"

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd)) 
    sys.exit(1)

def downloadDojo(thePath):
    """Download the Dojo JS toolkit"""
    DOJO_URL = "http://download.dojotoolkit.org/release-{0}/dojo-release-{0}.tar.gz".format(DOJO_VERSION)

    dojoFile =os.path.join(thePath,
                           "dojo-release-{0}.tar.gz".format(DOJO_VERSION))

    dojopath = os.path.join(thePath, "dojo")

    if os.path.exists(dojoFile):
        print "Dojo Exists"        
    else:
        print "Downloading Dojo"
        urllib.urlretrieve(DOJO_URL,dojoFile)
        dojoTar = tarfile.open(dojoFile)
        dojoTar.extractall(thePath)

        #Overwrite any existing version
        if os.path.isdir(dojopath):
            print("Directory Exists")
            shutil.rmtree(dojopath)

        dojosource =os.path.join(thePath,
                                 "dojo-release-{0}".format(DOJO_VERSION))
        print "Source {0} Dest {1}".format(dojosource,
                                           dojopath)
                            
        shutil.copytree(dojosource,
                        dojopath)

    myWidget = os.path.join(dojopath,"MyWidgets")
    myexists = os.path.exists(myWidget)
    if not myexists:
        fullPath = os.path.join(myWidget,"form")
        os.makekdirs(fullPath)
        shutil.copy("cogentviewer/static/DateTimeBox.js",fullPath)
        
    #Then check for the dgrid etc modules
    dgridpath = os.path.join(dojopath,"dgrid")
    dexists = os.path.exists(dgridpath)
    print "Check for {0} {1}".format(dgridpath,dexists)
    
    if not dexists:
        print "No Dgrid"
        subprocess.call(["git",
                         "clone",
                         "https://github.com/SitePen/dgrid.git",
                         dgridpath])


    #And dgrid dependencies
    thepath = os.path.join(dojopath,"xstyle")
    exists = os.path.exists(thepath)
    print "Check for {0} {1}".format(thepath,exists)
    if not exists:
        print "No X Style"
        subprocess.call(["git",
                         "clone",
                         "https://github.com/kriszyp/xstyle.git",
                         thepath])

    thepath = os.path.join(dojopath,"put-selector")
    exists = os.path.exists(thepath)
    print "Check for {0} {1}".format(thepath,exists)
    if not exists:
        print "No Put Selector"
        subprocess.call(["git",
                         "clone",
                         "https://github.com/kriszyp/put-selector.git",
                         thepath])    


def downloadJQuery(thePath):
    theurl = "http://code.jquery.com/jquery-{0}.min.js".format(JQUERY_VERSION)

    thefile =os.path.join(thePath,
                          "jquery-{0}.min.js".format(JQUERY_VERSION))

    basepath = os.path.join(thePath, "jquery.min.js")

    if os.path.exists(thefile):
        print "Jquery Exists"        
    else:
        print "Downloading Jquery"
        urllib.urlretrieve(theurl,thefile)
    
    shutil.copy(thefile,
                basepath)

def downloadHighCharts(thePath):
    """Grab the latest Highcharts / Highstock Librarys"""
    print "Check for Highcharts"

    #DOJO_URL = "http://download.dojotoolkit.org/release-{0}/dojo-release-{0}.tar.gz".format(DOJO_VERSION)
    theurl = "http://www.highcharts.com/downloads/zips/Highcharts-{0}.zip".format(HIGHCHARTS_VERSION)

    thefile =os.path.join(thePath,
                          "Highcharts-{0}.zip".format(HIGHCHARTS_VERSION))

    basepath = os.path.join(thePath, "Highcharts")

    if os.path.exists(thefile):
        print "Highcharts Exists"        
    else:
        print "Downloading Highcharts"
        urllib.urlretrieve(theurl,thefile)

        thezip = zipfile.ZipFile(thefile)
        thezip.extractall(basepath)

    theurl = "http://www.highcharts.com/downloads/zips/Highstock-{0}.zip".format(HIGHSTOCK_VERSION)

    thefile =os.path.join(thePath,
                          "Highstock-{0}.zip".format(HIGHSTOCK_VERSION))

    basepath = os.path.join(thePath, "Highstock")

    if os.path.exists(thefile):
        print "Highstock Exists"        
    else:
        print "Downloading HighStock"
        urllib.urlretrieve(theurl,thefile)

        thezip = zipfile.ZipFile(thefile)
        thezip.extractall(basepath)



def main(argv=sys.argv):
    print "Downloading"

    thePath = os.path.relpath(os.path.join("cogentviewer","jslibs"))
   
    #Create a JS directory if it doesnt exits
    if not os.path.exists(thePath):
        print "Exists {0}".format(os.path.exists(thePath))
        os.makedirs(thePath)

    downloadDojo(thePath)
    downloadHighCharts(thePath)
    downloadJQuery(thePath)
    #if len(argv) != 2:
    #    usage(argv)
    #config_uri = argv[1]
    #setup_logging(config_uri)
    #settings = get_appsettings(config_uri)
