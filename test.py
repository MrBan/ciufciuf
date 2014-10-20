#!/usr/bin/env python
"""Trenitalia test module"""

from tabulate import tabulate

from Trenitalia import Trenitalia

if __name__ == "__main__":
    TP = Trenitalia({"dep": "Firenze S. M. Novella",
                     "arr": "Milano Centrale",
                     "date": "21-11-2014",
                     # "time": "07",
                     "nAdults": "1",
                     "code": "9502"})

    RES = TP.find_page()

    for train in RES:
        print "Train Code:\t" + train["trainCode"]
        print "Departure:\t" + train["depTime"]
        print "Arrival:\t" + train["arrTime"]
        print "Duration:\t" + train["duration"]
        table = list()
        for pr in train["prices"]:
            row = [pr["fareType"]]
            for x in pr["farePrices"]:
                row.append(x["price"])
            table.append(row)
        print
        print tabulate(table, headers=TP.COMFORTS)
