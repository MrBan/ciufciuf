# -*- coding: utf-8 -*-
"""Trenitalia test module"""

from time import gmtime, strftime
from Trenitalia import Trenitalia

if __name__ == "__main__":
    TP = Trenitalia({"dep": "Firenze S. M. Novella",
                     "arr": "Milano Centrale",
                     "date": "15-01-2015",
                     "time": "07",
                     "nAdults": "1",
                     "code": "9502"})

    RES = TP.find_page()
    if len(RES) > 0:
        print strftime("%Y-%m-%d %H:%M:%S", gmtime())
        TRAIN = RES[0]
        for pr in TRAIN["prices"]:
            x = [str(y["price"]) for y in pr["farePrices"]]
            print "{0},{1};".format(pr["fareType"], ",".join(x))
