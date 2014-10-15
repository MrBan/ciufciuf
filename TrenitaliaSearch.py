"""Manage Trenitalia Search"""

import urllib
import httplib
from urlparse import urlparse


class TrenitaliaSearch(object):
    """Trenitalia Search Class"""

    def __init__(self):
        self._search_host = "www.lefrecce.it"
        self._search_path = "/B2CWeb/searchExternal.do?parameter=initBaseSearch"

    def search_train(self, config):
        """perform search"""

        params = urllib.urlencode({'isRoundTrip': 'false',
                                   'departureStation': config["dep"],
                                   'arrivalStation': config["arr"],
                                   'departureDate': config["date"],
                                   'departureTime': config["time"],
                                   'noOfAdults': config["nAdults"],
                                   'selectedTrainType': 'frecce',
                                   'noOfChildren': '0'})
        headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9"
               ",image/webp,*/*;q=0.8"}

        # first request to get Session code
        conn = httplib.HTTPSConnection(self._search_host)

        conn.request("POST", self._search_path, params, headers)
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
