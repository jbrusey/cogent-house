.. _rest-interface:

***************
Rest Interface
***************

A REST interface has been implmented. This will return JSON formatted
representation of the data to help external applications extract the data.

This can also be used to upload data to the datastroe without having to rely on
protocols other than HTTP for instance faculitating the upload of data without
the need to rely on specialised tools or protocols.

URL Structure
==============

The basic url strucutre for the rest interface is:

http://<host>/rest/{table}/{identifier}

for example this url will return the deployment with an Id of One.

http://www.coventry.ac.uk/webinterface/rest/deployment/1


Request Overview
-----------------

+---------------+-------------+-------------------------+--------------------------+-------------------------+
| URL           | HTTP Method | Functionality           | Return Body              | Return Headers          |
+===============+=============+=========================+==========================+=========================+
| /<table>/     | GET         | Return all Objects      | [Objects]                | 200 (Ok)	             |
+---------------+-------------+-------------------------+--------------------------+-------------------------+
| /<table>/<id> | GET         | Return object with <id> | Object	           | 200 (Ok) 404 (Not Found)|
+---------------+-------------+-------------------------+--------------------------+-------------------------+
| /<table>/     | POST        | Add a new object        | New Object               | 201 + Location URL      |
+---------------+-------------+-------------------------+--------------------------+-------------------------+
| /<table>/<id> | PUT         | Update object with <id> | Updated Object           | 201		     |
+---------------+-------------+-------------------------+--------------------------+-------------------------+
| /<table>/<id> | DELETE      | Delete object with <id> |                          | 204		     |
+---------------+-------------+-------------------------+--------------------------+-------------------------+


Using the REST interface
==========================

To demonstrate the Rest interface we will make use of *python-rest-client*::

    >>> import restful_lib
    >>> base_url = "http://127.0.0.1:6543/rest/"
    >>> conn = restful_lib.Connection(base_url)

This lets us make requests and examine the returned objects using the *.request_<method>* functions::

     >>> out = conn.request_get("deployment/")
     >>> out
     {u'body': u'[{"startDate": null, "endDate": null, "description": null, "__table__": "Deployment", "id": 1, "name": "PushTest"}, {"startDate": "2012-04-02T15:35:06", "endDate": "2012-04-04T15:35:06", "description": "testing", "__table__": "Deployment", "id": 2, "name": "test"}]', u'headers': {'status': '200', 'content-length': '265', 'content-location': u'http://127.0.0.1:6543/rest/deployment/', 'server': 'PasteWSGIServer/0.5 Python/2.7.1+', 'date': 'Mon, 21 May 2012 08:08:12 GMT', 'content-type': 'application/json; charset=UTF-8'}}


Fetching Items
---------------

Fetch all Items in the *deployment* table::

      #(GET) /rest/deployment/
      >>> out = conn.request_get("deployment/")
      ... 
      >>> jOut = json.loads(out["body"])
      >>> pprint.pprint(jOut)
      [{u'__table__': u'Deployment',
        u'description': None,
	u'endDate': None,
	u'id': 1,
	u'name': u'PushTest',
	u'startDate': None},
	{u'__table__': u'Deployment',
	u'description': u'testing',
	u'endDate': u'2012-04-04T15:35:06',
	u'id': 2,
	u'name': u'test',
	u'startDate': u'2012-04-02T15:35:06'}]

Fetch Item with Id of 1 in the *house* table::

      (GET) HTTP://...rest/house/1
      >>> out = conn.request_get("house/1")
      >>> jOut = json.loads(out["body"])
      >>> print jOut
      [{u'startDate': None, u'endDate': None, u'__table__': u'House', u'deploymentId': 1, u'address': u'Push Address', u'id': 1}]


We can then deal with the data in one of two ways

Manual Conversion
~~~~~~~~~~~~~~~~~~

convert the body from a string to a list of JSON encoded objects::

     >>> objList = json.loads(out["body"])
     >>> objList
     [{u'startDate': None, u'endDate': None, u'description': None, u'__table__': u'Deployment', u'id': 1, u'name': u'PushTest'}, {u'startDate': u'2012-04-02T15:35:06', u'endDate': u'2012-04-04T15:35:06', u'description': u'testing', u'__table__': u'Deployment', u'id': 2, u'name': u'test'}]
     >>> objList[1]
     {u'startDate': u'2012-04-02T15:35:06', u'endDate': u'2012-04-04T15:35:06', u'description': u'testing', u'__table__': u'Deployment', u'id': 2, u'name': u'test'}

     
And if the model classes are available, convert to the appropriate model:

    >>> theDeployment = models.Deployment()
    >>> theDeployment.fromJSON(objList[0])


Using the table object generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We could also use the JSON to Object generator.

   >>> out = conn.request_get("deployment/")
   >>> #And do something like this
   >>> jsonBody = json.loads(out["body"] )
   >>> theGen = models.clsFromJSON(jsonBody)
   >>> for item in theGen:
   ...     print item
   ... 
   Deployment: 1 PushTest None - None
   Deployment: 2 test 2012-04-02 15:35:06 - 2012-04-04 15:35:06
   >>> 
   >>> # Or Like This
   >>> jsonBody = json.loads(out["body"])
   >>> theList = list(models.clsFromJSON(jsonBody))
   >>> theList
   [<cogentviewer.models.deployment.Deployment object at 0x90dcaac>, <cogentviewer.models.deployment.Deployment object at 0x91635ec>]
   >>> 

Adding New Items
------------------

To add a new Item we simply create a <column>:<value> dictionary of the new
object, JSON encode it (to stringify) and send it as a POST request to the
relevant table.  If we are directly working with the database models, we can use
the asDict() method to encode the object::

    >>> theHouse = models.House(address = "10 Greenhill Street",startDate = datetime.datetime.now())
    >>> jsonString = json.dumps(theHouse.toDict())
    >>> out = conn.request_post("house/",body=jsonString)
    >>> out
    {u'body': u'{"startDate": "2012-05-21T12:11:36.800067", "endDate": null, "__table__": "House", "deploymentId": null, "address": "10 Greenhill Street", "id": 4}', u'headers': {'status': '201', 'content-length': '147', 'server': 'PasteWSGIServer/0.5 Python/2.7.1+', 'location': 'http://127.0.0.1:6543/rest/house/4', 'date': 'Mon, 21 May 2012 11:13:00 GMT', 'content-type': 'application/json; charset=UTF-8'}}

This method will return the new object as a JSON string in the body of the request,
additionally, in the headers there the 'location' field, will return a valid REST GET url for the new object. 


If the model classes are not avaliable, we can also make use of a dictionary representation of the object.::

    >>> theHouse = {"deploymentId":1,"address":"Test","startDate" : datetime.datetime.now().isoformat()}
    >>> jsonString = json.dumps(theHouse)
    >>> out = conn.request_post("house/",body=jsonString)
    >>> out
    {u'body': u'{"startDate": "2012-05-21T11:57:01.200086", "endDate": null, "__table__": "House", "deploymentId": 1, "address": "Test", "id": 3}', u'headers': {'status': '201', 'content-length': '129', 'server': 'PasteWSGIServer/0.5 Python/2.7.1+', 'location': 'http://127.0.0.1:6543/rest/house/3', 'date': 'Mon, 21 May 2012 11:02:25 GMT', 'content-type': 'application/json; charset=UTF-8'}}

.. note::

   Datetime objects need to be encoded in the IsoFormat to allow JSON'ification.

Updating Items
---------------

To update an item, we use a PUT request.  This should also include a JSON encoded dictionary of <column>:<value> in the request body (request parameters).
And be set to the url of *<table>/<id>*
Continuing the example above::

    >>> theHouse.endDate = datetime.datetime.now()
    >>> print theHouse
    House 4  10 Greenhill Street  2012-05-21 12:11:36.800067-2012-05-21 12:15:31.592049
    >>> jsonString = json.dumps(theHouse.toDict())
    #As the House ID is 4 our URL String (<table>/<id>) == house/4
    >>> out = conn.request_put("house/4",body=jsonString)
    >>> out
    {u'body': u'{"startDate": "2012-05-21T12:11:36.800067", "endDate": "2012-05-21T12:15:31.592049", "__table__": "House", "deploymentId": null, "address": "10 Greenhill Street", "id": 4}', u'headers': {'status': '201', 'content-length': '171', 'server': 'PasteWSGIServer/0.5 Python/2.7.1+', 'location': 'http://127.0.0.1:6543/rest/house/4', 'date': 'Mon, 21 May 2012 11:17:21 GMT', 'content-type': 'application/json; charset=UTF-8'}}



Deleting Items
---------------

To delete items we use a DELETE reuest, to the url of *<table>/<id>* If successfully deleted the service sould return a status of 204::

   >>> out = conn.request_delete("house/4")
   >>> out
   {u'body': u'', u'headers': {'date': 'Mon, 21 May 2012 11:20:19 GMT', 'status': '204', 'content-length': '4', 'content-type': 'application/json; charset=UTF-8', 'server': 'PasteWSGIServer/0.5 Python/2.7.1+'}}
   >>> 


Request Parameters
===================

We can also supply arguments to perform searching, fetch a subset of the data,  and sorting.

Getting a subset of the data
------------------------------

To fetch a subset of the data (for instance for pagination) the Rest interface supports the *Range* header.

The range header is used with a GET request, and takes the form *range: 'items=<start>-<end>'* for example *range: items=1-5*
To help with pagination, this request will also return a Content-Range header, of the form *Content-Range: items <start>-<end>/<total>*

For Example to get the first 5 items from the deployment table::

    >>> rangeArg = "items=0-5"
    >>> out = self.rest.request_get("/deployment/",headers={"Range":rangeArg})


Querying
=========

I have also implmented a simple query language, this makes use query parameters appended to the URL

The Key, Value pairs used in the query language are of the form *<column>:<value>*,  for example, if we wish to filter the Deployment table to only include Id 3 we could use the query string *?id=3*  when urlencoded this would give the Rest URL of /rest/Deployment/?id=3

This query language can be used with:

* GET to search for objects 
* POST,PUT queries to add / update items matching a certain criteria

.. note::

   The Date format used is reasonaby flexible, accepting anything the dateutil.parser function will
   However, I would expect to use either datetime.isoformat() strings for full dates,
   Or a simple string of the form <YYYY>-<MM>-<DD> when just a date range is specified.


+-------------+-----------------------+----------------------------+-----------------------------------------------------------+
|  Modifier   |  Function             | Python Rest Client Example | Url Encoded Example                                       |
+=============+=======================+============================+===========================================================+
| <val>	      | equals                | {id:3}			   | http://127.0.0.1:6543/rest/house/?id=3                    |
+-------------+-----------------------+----------------------------+-----------------------------------------------------------+
| le_<val>    | less than or equal    | {id:"le_3"}	           | http://127.0.0.1:6543/rest/house/?id=lt_3                 |
+-------------+-----------------------+----------------------------+-----------------------------------------------------------+
| lt_<val>    | Less than	      | {id:"lt_3"}	           | http://127.0.0.1:6543/rest/house/?id=le_3                 |
+-------------+-----------------------+----------------------------+-----------------------------------------------------------+
| ge_<val>    | greater than or equal | {id:"ge_3"}		   | http://127.0.0.1:6543/rest/house/?startDate=gt_2012-05-20 |
+-------------+-----------------------+----------------------------+-----------------------------------------------------------+
| gt_<val>    | Greater than          | {id:"gt_3"}                | http://127.0.0.1:6543/rest/house/?startDate=gt_2012-05-20 |
+-------------+-----------------------+----------------------------+-----------------------------------------------------------+

Query Examples
---------------

Based on the following simple dataset::

    >>> out = conn.request_get("/house/")
    >>> pprint.pprint(json.loads(out["body"]))
    [{u'__table__': u'House',
      u'address': u'135',
      u'deploymentId': 1,
      u'endDate': u'2012-05-22T12:00:00',
      u'id': 1,
      u'startDate': u'2012-04-01T12:00:00'},
     {u'__table__': u'House',
       u'address': u'Test',
       u'deploymentId': 1,
       u'endDate': u'2012-05-22T12:00:00',
       u'id': 2,
       u'startDate': u'2012-05-21T11:57:01.200086'},
     {u'__table__': u'House',
       u'address': u'Test',
       u'deploymentId': 2,
       u'endDate': None,
       u'id': 3,
       u'startDate': u'2012-05-23T11:57:01.200086'}]
    >>> 
     
Filter all properties that belong to deployment Id==1::

   >>> params = {'id':1}
   >>> out = conn.request_get("/house/",args=params)
   >>> pprint.pprint(json.loads(out["body"]))
   [{u'__table__': u'House',
     u'address': u'135',
     u'deploymentId': 1,
     u'endDate': u'2012-05-22T12:00:00',
     u'id': 1,
     u'startDate': u'2012-04-01T12:00:00'}]
   >>> 


Or All Houses with an address of "Test"::

   >>> params = {'address':"Test"}
   >>> out = conn.request_get("/house/",args=params)
   >>> pprint.pprint(json.loads(out["body"]))
   [{u'__table__': u'House',
     u'address': u'Test',
     u'deploymentId': 1,
     u'endDate': u'2012-05-22T12:00:00',
     u'id': 2,
     u'startDate': u'2012-05-21T11:57:01.200086'},
   {u'__table__': u'House',
     u'address': u'Test',
     u'deploymentId': 2,
     u'endDate': None,
     u'id': 3,
     u'startDate': u'2012-05-23T11:57:01.200086'}]
   >>> 


Properties with both an address of Test, that were in deployment 1::

    >>> params = {'address':"Test","deploymentId":1}
    >>> out = conn.request_get("/house/",args=params)
    >>> pprint.pprint(json.loads(out["body"]))
    [{u'__table__': u'House',
      u'address': u'Test',
      u'deploymentId': 1,
      u'endDate': u'2012-05-22T12:00:00',
      u'id': 2,
      u'startDate': u'2012-05-21T11:57:01.200086'}]
    >>> 

Houses with a start date of after Midnight 21st May 2012 or later::

   >>> theDate = datetime.datetime(2012,5,21,00,00)
   >>> params = {"startDate":"gt_{0}".format(theDate)}
   >>> out = conn.request_get("/house/",args=params)
   >>> pprint.pprint(json.loads(out["body"]))
   [{u'__table__': u'House',
     u'address': u'Test',
     u'deploymentId': 1,
     u'endDate': u'2012-05-22T12:00:00',
     u'id': 2,
     u'startDate': u'2012-05-21T11:57:01.200086'},
   {u'__table__': u'House',
     u'address': u'Test',
     u'deploymentId': 2,
     u'endDate': None,
     u'id': 3,
     u'startDate': u'2012-05-23T11:57:01.200086'}]


Houses with a start date between the 20/5/2012 and the 22/5/2012::
     
     >>> theEnd = datetime.datetime(2012,5,23)
     >>> params = {"startDate":"ge_2012-05-20","endDate":"le_{0}".format(theEnd)}
     >>> out = conn.request_get("/house/",args=params)
     >>> pprint.pprint(json.loads(out["body"]))
     [{u'__table__': u'House',
       u'address': u'Test',
       u'deploymentId': 1,
       u'endDate': u'2012-05-22T12:00:00',
       u'id': 2,
       u'startDate': u'2012-05-21T11:57:01.200086'}]
     >>> 


Updating Items using a query
-----------------------------

If we are unsure of object Id's it is possible to update items using a query string::

     theDeployment = models.Deployment(id=2,
                                       name="Second Deployment",
                                       description="Updated")

     theUrl = "deployment/?{0}".format(urllib.urlencode({"id":2}))

     out = self.rest.request_put(theUrl,body=json.dumps(theDeployment.toDict()))



"Bulk" Uploads
===============

If there are many items to upload, and we are less concerned about getting
object ID's back (for instance in the case of Readings) then we can use the bulk
upload function. at URL **/rest/bulk/** 

Currently this takes a JSONified list of objects in the body, and will return
201 if successfull and 404 if there is an error::

     now = datetime.datetime.now()
     readingList = []

     for x in range(10):
        theReading = models.Reading(time=now+datetime.timedelta(seconds=x),
                                    nodeId=1,
                                    typeId=1,
                                    locationId=1,
                                    value=x)

        readingList.append(theReading)

     jsonBody = json.dumps([x.toDict() for x in readingList])

     out = self.rest.request_post("bulk/",body=jsonBody)
 




   
