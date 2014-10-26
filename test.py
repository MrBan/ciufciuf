#!/usr/bin/env python
"""Trenitalia test module"""

from datetime import date, timedelta

from Trenitalia import Trenitalia

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

if __name__ == "__main__":
    START = date.today()
    END = START + timedelta(30)

    for d in daterange(START, END):
        TP = Trenitalia({"dep": "Firenze S. M. Novella",
                         "arr": "Milano Centrale",
                         "date": d.strftime("%d-%m-%Y"),
                         "time": "07",
                         "nAdults": "1",
                         "code": "9502"})

        RES = TP.find_page()
        if len(RES) > 0:
            train = RES[0]
            table = list()
            print d.strftime("%A %d %B %Y")
            for pr in train["prices"]:
                if pr["fareType"] == "SUPER ECONOMY":
                    for x in pr["farePrices"]:
                        if x["price"] != "N/A":
                            print (d.strftime("%A %d %B %Y") + " " + x["comfort"]+ " " +str(x["price"]))
                            break
                    else:
                        continue
                    break
            else:
                continue
            break
    print "The end"
