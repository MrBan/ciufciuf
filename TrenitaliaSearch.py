"""Manage Trenitalia Search"""

import urllib
import httplib
from urlparse import urlparse

class TrenitaliaSearch(object):
    """Trenitalia Search Class"""

    def __init__(self):
        self._search_host = "www.lefrecce.it"
        self._init_path = "/B2CWeb/searchExternal.do?parameter=initBaseSearch"

    def get_page(self, config):
        """Search train solutions

        Perform search request on Trenitalia Web service. For the moment the
        result includes only the first page.

        Args:
            config: a dictionary containing search parameters. For example:
                {
                    'dep': 'Milano Centrale',
                    'arr': 'Bologna Centrale',
                    'date': '15-10-2014',
                    'time': '08',
                    'nAdults': '1',
                }

        Returns:
            An object containing the HTML code of the first result page.
        """

        params = urllib.urlencode({'isRoundTrip': 'false',
                                   'departureStation': config["dep"],
                                   'arrivalStation': config["arr"],
                                   'departureDate': config["date"],
                                   'departureTime': config["time"],
                                   'noOfAdults': config["nAdults"],
                                   'selectedTrainType': 'frecce',
                                   'noOfChildren': '0'})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/html,application/xhtml+xml,application/xml;"
                             "q=0.9,image/webp,*/*;q=0.8"}

        # first request to get Session code
        conn = httplib.HTTPSConnection(self._search_host)

        conn.request("POST", self._init_path, params, headers)
        resp = conn.getresponse()
        location = resp.getheader("location")
        cookie = resp.getheader("set-cookie")
        location_obj = urlparse(location)

        # second request to retrieve results
        conn = httplib.HTTPSConnection(self._search_host)
        conn.request("GET", location_obj.path+"?"+location_obj.query,
                     headers={'Cookie': cookie})
        resp = conn.getresponse()
        html = resp.read()
        conn.close()

        return html

    def get_next_page(self):
        """Get next result page"""
        # TODO
        html = ""
        return html
