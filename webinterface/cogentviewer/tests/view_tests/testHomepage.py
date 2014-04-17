import datetime

from cogentviewer.views import homepage
import cogentviewer.tests.base as base
import cogentviewer.models as models

NAVBAR = homepage.NAVBAR

class HomepageTest(base.FunctionalTest):
    warningmsg = "This may have failed due to the use of a non clean testing database"

    def testhomepage(self):
        """Does the homepage load"""
        res = self.testapp.get("/")
        self.assertEqual(res.status_int, 200)
        self.assertEqual(res.content_type,"text/html")
        res.mustcontain("<title>Homepage</title>")

    #@unittest.skip
    # def testhomepagecontent(self):
    #     res = self.testapp.get("/")

    #     bs = res.html

    #     #Check each table contains what we expect

    #     #There shold be one house
    #     thetab = bs.find("table", id="activehouses")
    #     #Count number of rows in the table body
    #     linecount = thetab.tbody.find_all("tr")
    #     self.assertEqual(len(linecount), 2)

    #     #no recenently heard nodes
    #     thetab = bs.find("table", id="recentnodes")
    #     linecount = thetab.tbody.find_all("tr")
    #     self.assertEqual(len(linecount), 1)

    #     #And Missing Nodes
    #     thetab = bs.find("table", id="missingnodes")
    #     #One new line per row + one newline for the tbody
    #     linecount = thetab.tbody.find_all("tr")
    #     self.assertEqual(len(linecount), 2)

    # #@unittest.skip
    # def testmissing(self):
    #     #Does updateing a nodestate affect the missing nodes correctly
    #     session = self.Session()
    #     #firstnode = session.query(models.Node).filter_by(id=838).first()

    #     now = datetime.datetime.now()

    #     newstate = models.NodeState(nodeId = 837,
    #                                 time=now)
    #     session.add(newstate)
    #     session.flush()
    #     session.commit()
    #     #session.close()

    #     #Fetch the page
    #     res = self.testapp.get("/")
    #     bs = res.html

    #     #We should now have one recenently heard node
    #     thetab = bs.find("table", id="recentnodes")
    #     linecount = thetab.tbody.find_all("tr")
    #     self.assertEqual(len(linecount), 1)

    #     #And one missing node
    #     thetab = bs.find("table", id="missingnodes")
    #     linecount = thetab.tbody.find_all("tr")
    #     self.assertEqual(len(linecount), 1)

    #     #Force Cleanup (We have to manually do this as the transaction does not work with multiple sessions)
    #     session = self.Session()
    #     newdate = now - datetime.timedelta(days = 30)
    #     theqry = session.query(models.NodeState).filter(models.NodeState.time > newdate)
    #     #print theqry.count()
    #     theqry.delete()
    #     session.flush()
    #     session.commit()
    #     #session.close()
