"""Functions to assist rendering output in Pyramid"""

import StringIO
import csv
import pyramid.renderers

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

class PandasJSONP(pyramid.renderers.JSONP):


    def __call__(self, value, system):
        request = system['request']
        #val =  json.dumps(value)
        val = value
        callback = request.GET.get(self.param_name)
        if callback is None:
            ct = 'application/json'
            body = val
        else:
            ct = 'application/javascript'
            body = '%s(%s)' % (callback, val)
        response = request.response
        if response.content_type == response.default_content_type:
            response.content_type = ct
        return body
    #return _render


    # def __call__(self, info):
    #     """ 
    #     Overloaded version of the builtin JSONP Renderer
    #     that allows objects that have already been converted to JSON
    #     (for example output of pandas dataframe) to be 
    #     used without double encoding

    #     Returns JSONP-encoded string with content-type
    #     ``application/javascript`` if query parameter matching
    #     ``self.param_name`` is present in request.GET; otherwise returns
    #     plain-JSON encoded string with content-type ``application/json``
    #     """
    #     def _render(value, system):
    #         request = system['request']
    #         #val =  json.dumps(value)
    #         val = value
    #         callback = request.GET.get(self.param_name)
    #         if callback is None:
    #             ct = 'application/json'
    #             body = val
    #         else:
    #             ct = 'application/javascript'
    #             body = '%s(%s)' % (callback, val)
    #         response = request.response
    #         if response.content_type == response.default_content_type:
    #             response.content_type = ct
    #         return body
    #     return _render
