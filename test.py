#!/usr/bin/env python

"""Trenitalia test module"""

from TrenitaliaSearch import TrenitaliaSearch
from TrenitaliaParser import TrenitaliaParser

if __name__ == "__main__":
    TS = TrenitaliaSearch()
    HTML = TS.search_train({"dep": "Milano Centrale",
                           "arr": "Bologna Centrale",
                           "date": "18-10-2014",
                           "time": "15",
                           "nAdults": "1"})
    F = open("sample.html", "w")
    F.write(HTML)
    F.close()

    PARSER = TrenitaliaParser(HTML)
    RES = PARSER.get_results()
    # f = 'type: {0}({1})\tleave: {2}\tarrive: {3}\tduration: {4}\tprice: {5}'
    # for x in result:
    #   print f.format(x['trainType'], x['trainCode'], x['depTime'],
    #           x['arrTime'], x['duration'], x['minPrice'])
    X = RES[0]
    for y in X["prices"]:
        print "type: " + y["fareType"]
        for z in y["farePrices"]:
            print "\ttype: " + z["comfort"] + "\t price: " + z["price"]
