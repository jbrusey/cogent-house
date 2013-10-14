import StringIO
import csv

class CSVRenderer(object):
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
