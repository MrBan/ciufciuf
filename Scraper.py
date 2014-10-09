import httplib
import urllib
from urlparse import urlparse, parse_qs
import re

# create a subclass and override the handler methods
class TrenitaliaParser():
	def __init__(self, html):
		self.result = list()
		self.soup = BeautifulSoup(html)

	def getResults(self):
		table = self.soup.find("table", class_="searchResult")
		for tr in table.find_all("tr"):
			if "id" in tr.attrs and tr.attrs["id"].startswith("trow"):
				tds = tr.find_all("td")
				depTd = tds[0]
				arrTd = tds[1]
				durTd = tds[2]
				trainTd = tds[3]
				priceTd = tds[4]
				
				opt = dict()
				opt["depTime"] = depTd.span.string
				opt["arrTime"] = arrTd.span.string
				opt["duration"] = durTd.span.string
				tmp = re.sub(r'[\t\n]*', '', trainTd.div.span.getText()).split()
				opt["trainType"] = tmp[0]
				opt["trainCode"] = tmp[1]
				self.result.append(opt)
		return self.result

class TrenitaliaSearch:
	def __init__(self):
		self.searchHost = "www.lefrecce.it"
		self.searchPath = "/B2CWeb/searchExternal.do?parameter=initBaseSearch"

	def SearchTrain(self, dep, arr, date, time):
		params = urllib.urlencode({'isRoundTrip': 'false',
					   'departureStation': dep,
					   'arrivalStation': arr,
					   'departureDate': date,
					   'departureTime': time,
					   'noOfAdults': '1',
					   'selectedTrainType': 'frecce',
					   'noOfChildren': '0'})
		headers = {"Content-type": "application/x-www-form-urlencoded",
			   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}

		# first request to get Session code
		conn = httplib.HTTPSConnection(self.searchHost)

		conn.request("POST", self.searchPath, params, headers)
		resp = conn.getresponse()
		location = resp.getheader("location")
		cookie = resp.getheader("set-cookie")
		location_obj = urlparse(location)

		# second request to retrieve results
		conn = httplib.HTTPSConnection(self.searchHost)
		conn.request("GET", location_obj.path+"?"+location_obj.query,
			     headers={'Cookie': cookie})
		resp = conn.getresponse()
		html = resp.read()
		conn.close()

		return html

if __name__ == "__main__":
	TS = TrenitaliaSearch()
	html = TS.SearchTrain("Milano Centrale",
			      "Bologna Centrale",
			      "18-10-2014",
			      "15")
	# f = open("sample.html", "w")
	# f.write(html)
	# f.close()

	parser = TrenitaliaParser(html)
	result = parser.getResults()
	f = 'type: {0}({1})\tleave: {2}\tarrive: {3}\tduration: {4}'
	for x in result:
		print f.format(x['trainType'], x['trainCode'], x['depTime'],
				x['arrTime'], x['duration'])
