#!/usr/bin/python

import requests
import hashlib
import sys
import glob
import zipfile
import argparse
import time
import os
import zlib

HOST_NAME = os.uname()[1]

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print(('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in list(req.headers.items())),
        req.body,
    )))

def hashfile(afile, hasher, blocksize=65536):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()

def send_file(fname, url, timeout=20.0):
    f = open(fname, 'rb')
    m = hashlib.md5()
    local_chk = hashfile(f, m)
    f.seek(0) # reset file pointer!!!
    files = {'userfile':(fname, f)}

    # actually send
    try:
        r = requests.post(url, files=files, timeout=timeout)
    except requests.exceptions.Timeout as e:
        print(e)
        return False

    if "Upload failed" in r.text:
        # couldn't move the file or some other server error
        return False

    # if we got here then the file was tx'd ok - check the checksum
    remote_chk = r.text.split(':')[1]
    if remote_chk == local_chk:
        return True
    else:
        return False


if __name__ == "__main__":
    # options - input directory, output directory, upload URL, number of retries
    parser = argparse.ArgumentParser(description="Upload BioSense files to the server")
    parser.add_argument("-u",
                        "--url",
                        metavar="URL",
                        default=None,
                        help="URL to post to (mandatory)")
    parser.add_argument("-o",
                        "--out-dir",
                        metavar="DIR",
                        default=".",
                        help="Output directory for files (default .)")
    parser.add_argument("-i",
                        "--in-dir",
                        metavar="DIR",
                        default=".",
                        help="Input directory for files (default .)")
    parser.add_argument("-t",
                        "--timeout",
                        metavar="SEC",
                        default=20.0,
                        help="Amount of time to wait without receiving bytes from server (default 20.0)")
    parser.add_argument("-r",
                        "--retries",
                        metavar="#",
                        default=3,
                        help="Number of times to retry files before giving up (default 3)")
    args = parser.parse_args()


    if args.url == None:
        print("You must supply a URL!")
        sys.exit()

    if args.in_dir == args.out_dir:
        print("Input and output directory cannot be the same")
        sys.exit()

    # program flow:
    # the radio switch on/off is controlled by a cron job

    # 1. add all .log files in 'in dir' into a zip file
    filelist = glob.glob('%s/*.log'%args.in_dir)
    
    time_string = time.strftime("%Y_%j_%H-%M", time.gmtime())
    zip_fname = "%s_%s.zip" % (time_string, HOST_NAME)
    zip_fname = "%s/%s"%(args.in_dir, zip_fname)
    if len(filelist) > 0:
        with zipfile.ZipFile(zip_fname, mode='w', compression=zipfile.ZIP_DEFLATED) as zfile:
            for f in filelist:
                fname = f.split('/')[-1]
                # add to archive
                zfile.write(f, arcname=fname)
                # move files to output directory
                year,doy = fname.split('_')[0:2]
                new_fname = "%s/%s/%s/%s"%(args.out_dir, year, doy, fname)
                ensure_dir(new_fname)
                os.rename(f, "%s"%new_fname)
                
    # 2. try and send all zip files:
    ziplist = glob.glob('%s/*.zip'%args.in_dir)
    if len(ziplist) > 0:
        rtx_count = 0
        for f in ziplist:
            retval = False
            while retval == False and rtx_count < int(args.retries):
                print("Sending %s"%f)
                retval = send_file(f, args.url, timeout=float(args.timeout))
                if retval == True:
                    print("Success!")
                    os.remove(f)
                    if rtx_count > 0:
                        rtx_count -= 1
                else:
                    print("Send failed! %d tries %d max"%(rtx_count+1, int(args.retries)))
                    rtx_count += 1
