import sqlalchemy

#Import Pyramid Meta Data
import meta
import datetime
import dateutil 

class PushStatus(meta.Base, meta.InnoDBMix):
    """Debugging table to hold status of push operations"""
    __tablename__ = "Pushstatus"

    #Pk
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    #Time the push was received
    time = sqlalchemy.Column(sqlalchemy.DateTime)

    #local time
    localtime = sqlalchemy.Column(sqlalchemy.DateTime)

    #Hostname of push script
    hostname = sqlalchemy.Column(sqlalchemy.String(25))

    #Version string
    version = sqlalchemy.Column(sqlalchemy.String(20))


    def from_json(self, jsonobj):
        """Update the object using a JSON string

        Overload the version from meta to ensure that the time string is
        set to the current time
        """

        if type(jsonobj) == str:
            jsonobj = json.loads(jsonobj)
        if type(jsonobj) == list:
            jsonobj = jsonobj[0]
        #For each column in the table
        for col in self.__table__.columns:
            #Check to see if the item exists in our dictionary
            value = jsonobj.get(col.name, None)

            #Fix missing values
            #if col.name == "locationId":
            #    setattr(self,col.name,newValue)
            if value is None:
                pass
            else:
                #Convert if it is a datetime object
                if isinstance(col.type, sqlalchemy.DateTime) and value:
                    value = dateutil.parser.parse(value, ignoretz=True)
                #And set our variable
            setattr(self, col.name, value)

        self.time = datetime.datetime.now()

    def pandas(self):
        """Format object for conversion to pandas"""
        outdict = {"hostname": self.hostname,
                   "time": self.time,
                   "localtime": self.localtime}
        return outdict
