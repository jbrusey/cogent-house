"""
Main Setup file for the Pylons application

@author: Dan Goldsmith
@version: 0.3
@since May 2013
"""
#SQLA
from sqlalchemy import engine_from_config

#Pyramid
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.renderers import JSONP

#My Stuff
from .models import meta
#from .models.meta import groupfinder as groupfinder
from cogentviewer.utils.security import groupfinder as groupfinder


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    #Setup the Config
    #config = Configurator(settings=settings)
    config = Configurator(settings=settings,
                    root_factory="cogentviewer.utils.security.RootFactory")


    authentication_policy = AuthTktAuthenticationPolicy("seekrit",
                                                        callback=groupfinder)
    authorization_policy = ACLAuthorizationPolicy()

    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)

    #Scan our models directory to "automagically" import everything
    config.scan("cogentviewer.models")

    #Start the Database
    engine = engine_from_config(settings, 'sqlalchemy.')
    meta.Session.configure(bind=engine)
    meta.DBSession.configure(bind=engine)
    meta.Base.metadata.bind = engine

    config.add_renderer(name='csv',
                        factory='cogentviewer.renderers.CSVRenderer')

    config.add_renderer(name="pancsv",
                        factory='cogentviewer.renderers.PandaCSVRenderer')

    config.add_renderer(name="pandas_jsonp",
                        factory='cogentviewer.renderers.PandasJSONP')



    #Static Views
    config.add_static_view('static', 'cogentviewer:static', cache_max_age=3600)
    #Javascript Libs
    config.add_static_view('jslibs', 'cogentviewer:jslibs')
    

    #And the Rest of the Views can be setup here
    config.add_route('home', '')
    config.add_route("timeseries", "/timeseries")
    config.add_route("exposure", "/exposure")
    config.add_route("electricity", "/electricity")
    config.add_route("status", "/status")
    config.add_route("admin", "/admin")
    config.add_route("databrowser", "/data")
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('register', '/register')
    config.add_route('user', '/user/{id:.*}')
    config.add_route("serverstatus", "/serverstatus")
    config.add_route("export", "/export")
    config.add_route("report", "/report")

    config.add_route("housestatus", "/housestatus")
    config.add_route("housedetail", "/housedetail/{id}")

    #New Graphing Stuff
    config.add_route("newgraphs", "/newgraphs")
    
    #Debugging
    config.add_route("nodestatus", "/nodestatus")
    config.add_route("housedebug", "/housedebug/{id:.*}")
    config.add_route("pushdebug", "/pushdebug")
    config.add_route("heatmap", "/heatmap")
    config.add_route("netmap", "/netmap")

    #New Node Page
    config.add_route('node', '/node/{id:.*}')
    #Yields
    config.add_route("yield", "/yield/")
    #config.add_route("server", "/server")
    config.add_route("server", "/server")


    #Rest'y Stuff
    config.add_route("house", "/house/{id:.*}")
    config.add_view("cogentviewer.views.house.editHouse",
                    route_name="house")

    #Comfort
    config.add_route("comfort", "/comfort/{hid}/{tid}")

    #Fecthing data
    #Make sure we can serve JSONp
    config.add_renderer('jsonp', JSONP(param_name='callback'))

    config.add_route("jsonFetch", "jsonFetch")
    config.add_view("cogentviewer.views.jsonhandlers.jsonFetch",
                     route_name="jsonFetch",
                     renderer="jsonp")

    config.add_route("jsonnav", "jsonnav")
    config.add_view("cogentviewer.views.jsonhandlers.jsonnav",
                    route_name="jsonnav",
                    renderer="jsonp")

    config.add_route("genericRest", "rest/{theType}/{id:.*}")
    config.add_view("cogentviewer.views.restService.genericRest",
                    route_name="genericRest",
                    renderer="json")

    config.add_route("summaryRest", "sumRest/{theType}/{id:.*}")
    config.add_view("cogentviewer.views.restService.summaryRest",
                    route_name="summaryRest",
                    renderer="json")

    config.add_route("summaryRestDL", "sumRestDL/{theType}/{id:.*}")
    config.add_view("cogentviewer.views.restService.summaryRest",
                    route_name="summaryRestDL",
                    renderer="csv")

    config.add_route("restTest", "restTest/{id:.*}")
    config.add_view("cogentviewer.views.restService.restTest",
                    route_name="restTest",
                    renderer="json")

    config.add_route("chartTest", "chartTest/")
    config.add_view("cogentviewer.views.homepage.chartTest",
                    route_name="chartTest")

    config.add_route("electric", "elec/")
    config.add_view("cogentviewer.views.electricity.getElec",
                    route_name="electric",
                    renderer="csv")

    config.add_route("pv", "pv/")
    config.add_view("cogentviewer.views.electricity.getPv",
                    route_name="pv",
                    renderer="csv")

    config.add_route("newRest", "newRest/{id:.*}")
    #config.add_view("cogentviewer.views.newRest.RESTService",
    #                route_name="newRest")


    config.scan()
    return config.make_wsgi_app()

