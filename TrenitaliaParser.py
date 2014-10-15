"""Trenitalia _result parser"""

from bs4 import BeautifulSoup
import re

COMFORTS = ["STANDARD", "PREMIUM", "BUISNESS SALOTTINO",
            "BUISNESS AREA SILENZIO", "BUISNESS", "EXECUTIVE"]

class TrenitaliaParser(object):
    """Trenitalia result parser Class"""

    def __init__(self, html):
        self._result = list()
        self._soup = BeautifulSoup(html)

    def get_results(self):
        """Parse Trenitalia result page html

        Returns:
            A list of dicts containing all the train solutions with their
            prices. Each element of the list is in the following form:
            {
                'trainType': 'FRECCIAROSSA',
                'depTime': '15:12',
                'arrTime': '16:25',
                'duration': '1:13',
                'trainCode': '9953',
                'minPrice': '31.00',
                'prices': [
                    {
                        'fareType': 'BASE',
                        'farePrices': [
                            {
                                'comfort': 'STANDARD',
                                'price': '40.00'
                            },
                            {
                                'comfort': 'PREMIUM',
                                'price': '40.00'
                            },
                            ...
                            ...
                        ]
                    },
                    {
                        'fareType': 'ECONOMY',
                        'farePrices': [
                            ...
                        ]
                    },
                    ...
                    ...
                ]
            }
        """

        # result table
        table = self._soup.find("table", class_="searchResult")
        for res_tr in table.find_all("tr"):
            if not ("id" in res_tr.attrs and res_tr["id"].startswith("trow")):
                continue
            tds = res_tr.find_all("td")
            dep_td = tds[0]
            arr_td = tds[1]
            dur_td = tds[2]
            train_td = tds[3]
            price_td = tds[5]
            opt = dict()

            tmp = re.sub(r'[\t\n]*', '', train_td.div.span.getText()).split()

            # TODO: different train types have a different structure
            # at the moment parse only FRECCIAROSSA trains
            if tmp[0] != "FRECCIAROSSA":
                continue

            opt["trainType"] = tmp[0]

            opt["depTime"] = dep_td.span.string
            opt["arrTime"] = arr_td.span.string
            opt["duration"] = dur_td.span.string
            opt["trainCode"] = tmp[1]
            opt["minPrice"] = re.sub(r'[\s]', '', price_td.span.get_text())[:-1]
            opt["prices"] = list()
            for sib in res_tr.find_next_siblings("tr"):
                if not ("id" in sib.attrs and sib["id"].startswith("sd_")):
                    continue
                pr_tab = sib.table
                for idx, price_tr in enumerate(pr_tab.find_all("tr")):
                    # skip first two rows
                    if idx <= 1:
                        continue

                    pr_res = dict()
                    tds = price_tr.find_all("td")

                    if not (tds[0].span and tds[0].span.string):
                        continue

                    # BASE, ECONOMY ...
                    pr_res["fareType"] = tds[0].span.string.strip()
                    pr_res["farePrices"] = list()
                    for i in range(1, 7):
                        if not tds[i].span:
                            tmp = "none"
                        else:
                            tmp = re.sub(r'[\s]', '', tds[i].span.get_text())
                            if tmp == "SoldOut":
                                tmp = "none"
                            else:
                                tmp = tmp[:-1]
                        pr_res["farePrices"].append({"comfort": COMFORTS[i-1],
                                                     "price": tmp})

                    opt["prices"].append(pr_res)
                break
            self._result.append(opt)
        return self._result
