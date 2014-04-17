"""Functions to assist rendering output in Pyramid"""

import StringIO
import csv

class CSVRenderer(object):
    """Render a pyramid response as CSV"""
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        fout = StringIO.StringIO()

        writer = csv.writer(fout, delimiter=',')
        #writer = csv.writer(fout, delimiter=',',lineterminator="</br>")


        writer.writerow(value['header'])
        writer.writerows(value['rows'])

        resp = system['request'].response
        fname = value.get("fName","output.csv")
        resp.content_type = 'text/csv'
        #resp.content_disposition = 'attachment;filename="report.csv"'
        resp.content_disposition = 'attachment;filename="{0}"'.format(fname)
        return fout.getvalue()


class PandaCSVRenderer(object):
    """Render a Pandas Object as CSV"""
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        fout = StringIO.StringIO()

        df = value["data"]
        df.to_csv(fout)

        resp = system['request'].response
        fname = "Export.csv"
        resp.content_type = "text/csv"
        resp.content_disposition = "attachment;filename='{0}'".format(fname)
        #resp.content_disposition = "attachment;"
        return fout.getvalue()
