#!/usr/bin/env python
"""Trenitalia test module"""

from tabulate import tabulate

from TrenitaliaParser import TrenitaliaParser

if __name__ == "__main__":
    MYTRAINCODE = "9553"
    TP = TrenitaliaParser()

    RES = TP.find_page({"dep": "Milano Centrale",
                        "arr": "Firenze S. M. Novella",
                        "date": "18-10-2014",
                        "time": "18",
                        "nAdults": "1"})

    for train in RES:
        if train["trainCode"] == MYTRAINCODE:
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
