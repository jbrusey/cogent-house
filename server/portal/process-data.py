#!/usr/bin/python

import sys
import glob
import zipfile
import argparse
import os
import zlib
import json

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

if __name__ == "__main__":
    # options - input directory, output directory, upload URL, number of retries
    parser = argparse.ArgumentParser(description="Process files sent to Pulp portal")
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
    args = parser.parse_args()

    # program flow:
    # look for .zip files in directory
    # unzip any and move contents to archive folder {out_dir}/year/day/
    # also add lines of each file to a node's output file, and 'last' file
    # delete zip file

    # look for zip files
    ziplist = glob.glob('%s/*.zip'%args.in_dir)
    last_reading = {} # record last measurement for each node
    keep_file = False
    ziplist.sort(reverse=True)
    for zip_file in ziplist:
        print zip_file
        try:
            zfile = zipfile.ZipFile(zip_file, mode='r')
            for f in zfile.namelist():
                print f
                zfile.extract(f, path=args.in_dir)
                # move files to output directory
                year,doy = f.split('_')[0:2]
                new_fname = "%s/%s/%s/%s"%(args.out_dir, year, doy, f)
                try:
                    ensure_dir(new_fname)
                    os.rename("%s/%s"%(args.in_dir, f), "%s"%new_fname)
                except:
                    # don't go any further if we can't move the file
                    # certainly don't delete the archive!
                    sys.exit("Error moving file to new location.. exiting.")
                # now make files
                lines = zfile.open(f).readlines()
                for line in lines:
                    output = json.loads(line.strip('\n'))
                    try:
                        if float(last_reading[output['sender']]['server_time']) < float(output['server_time']):
                            last_reading[output['sender']] = output
                    except KeyError:
                        last_reading[output['sender']] = output

                    graph_file = open('%s/node_%s_gnu.csv'%(args.out_dir, output['sender']), 'a')
                    try:
                        graph_file.write("%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%u,%u,%u\n"%(\
                                output['server_time'], output['Temperature'], output['Humidity'],\
                                    output['ADC_0'], output['ADC_1'], output['ADC_2'], output['Voltage'],\
                                    output['parent'], output['rssi'], output['seq']))

                                    
                    except KeyError:
                        print output.keys()
                        print "bad zip file contents %s"%f
                        graph_file.close()
                        keep_file = True
                        break # stop processing the file
                    graph_file.close()
            zfile.close()
            if not keep_file:
                os.remove(zip_file)
            else:
                keep_file = False # reset it

        except zipfile.BadZipfile:
            print "Bad zipfile - cannot import"
            """
            move_fname = "%s/bad/%s"%(args.out_dir, zip_file)
            try:
                ensure_dir(move_fname)
                os.rename("%s/%s"%(args.in_dir, zip_file), "%s"%move_fname)
            except:
                # don't go any further if we can't move the file
                # certainly don't delete the archive!
                sys.exit("Error moving file to new location.. exiting.")
                """

    # now print out the last readings file
    for n in last_reading:
        nfile = open("/tmp/node_%s.log"%(n), 'w')
        nfile.write(json.dumps(last_reading[n])+"\n")
        nfile.close()
