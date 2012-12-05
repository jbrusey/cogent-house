"""
Main Setup file for the Pylons application

@author: Dan Goldsmith
@version: 0.1
@since August 2012
"""

from pyramid.config import Configurator
from sqlalchemy import engine_from_config


from pyramid.renderers import JSONP
from models import meta

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    #Setup the Config
    config = Configurator(settings=settings)

    #Add Formalchemy
    #onfig.include("pyramid_formalchemy")
    #config.include("fa.jquery")
    #config.include("cogentviewer.fainit")

    #Scan our models directory to "automagically" import everything
    config.scan("cogentviewer.models")

    #Start the Database
    engine = engine_from_config(settings, 'sqlalchemy.')
    meta.Session.configure(bind=engine)
    meta.Base.metadata.bind = engine

    config.add_renderer(name='csv',
                        factory='cogentviewer.renderers.CSVRenderer')

    #Static Views
    config.add_static_view('static', 'cogentviewer:static', cache_max_age=3600)
    #Javascript Libs
    config.add_static_view('jslibs','cogentviewer:jslibs')

    #And the Rest of the Views can be setup here
    config.add_route('home', '')
    config.add_view('cogentviewer.views.homepage.homepage',
                    route_name='home')


    #Displaying Database
    config.add_route("timeseries","/timeseries")
    config.add_view('cogentviewer.views.timeseries.timeseries',
                    route_name="timeseries")

    config.add_route("exposure","/exposure")
    config.add_view('cogentviewer.views.exposure.exposure',
                    route_name="exposure")

    config.add_route("electricity","/electricity")
    config.add_view("cogentviewer.views.electricity.electricity",
                    route_name="electricity")

    config.add_route("status","/status")
    config.add_view("cogentviewer.views.admin.status",
                    route_name="status")

    # #Administration Interface
    config.add_route("admin","/admin")
    config.add_view("cogentviewer.views.admin.admin",
                    route_name="admin")


    config.add_route("house","/house/{id:.*}")
    config.add_view("cogentviewer.views.house.editHouse",
                    route_name="house")

    config.add_route("databrowser","/data")
    config.add_view("cogentviewer.views.databrowser.main",
                    route_name="databrowser")

    # config.add_route("upload","/upload")
    # config.add_view("cogentviewer.views.transferdata.webupload",
    #                 route_name="upload")


    # config.add_route("procUpload","/procUpload")
    # config.add_view("cogentviewer.views.transferdata.processUpload",
    #                 route_name="procUpload")

    #Fecthing data
    #Make sure we can serve JSONp
    config.add_renderer('jsonp', JSONP(param_name='callback'))

    config.add_route("jsonFetch","jsonFetch")
    config.add_view("cogentviewer.views.jsonhandlers.jsonFetch",
                     route_name="jsonFetch",
                     renderer="jsonp")

    config.add_route("jsonRest","jsonRest/")
    config.add_view("cogentviewer.views.jsonhandlers.jsonRest",
                      route_name="jsonRest",
                      renderer="json")

    config.add_route("jsonRestP","jsonRest/{deployId}")
    config.add_view("cogentviewer.views.jsonhandlers.jsonRest",
                      route_name="jsonRestP",
                      renderer="json")

    config.add_route("jsonnav","jsonnav")
    config.add_view("cogentviewer.views.jsonhandlers.jsonnav",
                    route_name="jsonnav",
                    renderer="jsonp")


    #For Routes without an Id
    #config.add_route("deploymentRest","rest/deployment/")
    #config.add_view("cogentviewer.views.restService.deployment",
    #                route_name="deploymentRest",
    #                renderer="json")

    #For Routes with an Id
    #config.add_route("deploymentRestId","rest/deployment/{id}")
    # config.add_route("deploymentRestId","rest/deployment/{id:.*}")
    # config.add_view("cogentviewer.views.restService.deployment",
    #                 route_name="deploymentRestId",
    #                 renderer="json")


    config.add_route("genericRest","rest/{theType}/{id:.*}")
    config.add_view("cogentviewer.views.restService.genericRest",
                    route_name="genericRest",
                    renderer="json")




    config.add_route("summaryRest","sumRest/{theType}/{id:.*}")
    config.add_view("cogentviewer.views.restService.summaryRest",
                    route_name="summaryRest",
                    renderer="json")


    config.add_route("summaryRestDL","sumRestDL/{theType}/{id:.*}")
    config.add_view("cogentviewer.views.restService.summaryRest",
                    route_name="summaryRestDL",
                    renderer="csv")

#    config.add_route("modTree","modTree")
#    config.add_view("cogentviewer.views.jsonhandlers.modifyTree",
#                    route_name="modTree",
#                    renderer="jsonp")

    config.add_route("restTest","restTest/{id:.*}")
    #config.add_route("restTest","restTest.json")
    config.add_view("cogentviewer.views.restService.restTest",
                    route_name="restTest",
                    renderer="json")

    config.add_route("chartTest","chartTest/")
    config.add_view("cogentviewer.views.homepage.chartTest",
                    route_name="chartTest")

    config.add_route("electric","elec/")
    config.add_view("cogentviewer.views.electricity.getElec",
                    route_name="electric",
                    renderer="csv")

    config.add_route("pv","pv/")
    config.add_view("cogentviewer.views.electricity.getPv",
                    route_name="pv",
                    renderer="csv")
        

    config.add_route("newRest","newRest/{id:.*}")
    #config.add_view("cogentviewer.views.newRest.RESTService",
    #                route_name="newRest")

    config.scan()
    return config.make_wsgi_app()

