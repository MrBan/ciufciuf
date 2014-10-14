import httplib
import urllib
from urlparse import urlparse, parse_qs
import bs4
from bs4 import BeautifulSoup
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
				priceTd = tds[5]
				
				opt = dict()
				opt["depTime"] = depTd.span.string
				opt["arrTime"] = arrTd.span.string
				opt["duration"] = durTd.span.string
				tmp = re.sub(r'[\t\n]*', '',
					     trainTd.div.span.getText()).split()
				opt["trainType"] = tmp[0]
				opt["trainCode"] = tmp[1]
				opt["minPrice"] = re.sub(r'[\s]', '',
						         priceTd.span.get_text())[:-1]
				opt["prices"] = list()
				for sib in tr.find_next_siblings("tr"):
					if sib.has_attr("id") and sib["id"].startswith("sd_"):
						priceTab = sib.tbody
						# skip 2 tr
						priceTr = priceTab.find_next("tr").find_next("tr")
						for t in priceTr.find_next_siblings("tr"):
							p = dict()
							td1 = t.find_next("td")
							if td1.span and td1.span.string:
								p["fareType"] = td1.span.string.strip()
								p["farePrices"] = list()

								pr = td1.find_next_sibling("td")
								tmp = re.sub(r'[\s]', '', pr.span.get_text())[:-1]
								p["farePrices"].append({"type" : "STANDARD",
												 "price": tmp })

								pr = td1.find_next_sibling("td")
								tmp = re.sub(r'[\s]', '', pr.span.get_text())[:-1]
								p["farePrices"].append({"type" : "PREMIUM",
												 "price": tmp })

								pr = td1.find_next_sibling("td")
								tmp = re.sub(r'[\s]', '', pr.span.get_text())[:-1]
								p["farePrices"].append({"type" : "BUISNESS SALOTTINO",
												 "price": tmp })

								pr = td1.find_next_sibling("td")
								tmp = re.sub(r'[\s]', '', pr.span.get_text())[:-1]
								p["farePrices"].append({"type" : "BUISNESS AREA SILENZIO",
												 "price": tmp })

								pr = td1.find_next_sibling("td")
								tmp = re.sub(r'[\s]', '', pr.span.get_text())[:-1]
								p["farePrices"].append({"type" : "BUISNESS",
												 "price": tmp })

								pr = td1.find_next_sibling("td")
								tmp = re.sub(r'[\s]', '', pr.span.get_text())[:-1]
								p["farePrices"].append({"type" : "EXECUTIVE",
												 "price": tmp })

								opt["prices"].append(p)
						break

				self.result.append(opt)
		return self.result

class TrenitaliaSearch:
	def __init__(self):
		self.searchHost = "www.lefrecce.it"
		self.searchPath = "/B2CWeb/searchExternal.do?parameter=initBaseSearch"

	def SearchTrain(self, dep, arr, date, time, nAdults='1'):
		params = urllib.urlencode({'isRoundTrip': 'false',
					   'departureStation': dep,
					   'arrivalStation': arr,
					   'departureDate': date,
					   'departureTime': time,
					   'noOfAdults': nAdults,
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
	f = open("sample.html", "w")
	f.write(html)
	f.close()

	parser = TrenitaliaParser(html)
	result = parser.getResults()
	# f = 'type: {0}({1})\tleave: {2}\tarrive: {3}\tduration: {4}\tprice: {5}'
	# for x in result:
	# 	print f.format(x['trainType'], x['trainCode'], x['depTime'],
	# 			x['arrTime'], x['duration'], x['minPrice'])
	x = result[0]
	for y in x["prices"]:
		print("type: " + y["fareType"])
		for z in y["farePrices"]:
			print("\ttype: " + z["type"] + "\t price: " + z["price"])
