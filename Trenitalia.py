"""Trenitalia Service Module"""

from TrenitaliaSearch import TrenitaliaSearch
from bs4 import BeautifulSoup
import re

class Trenitalia(object):
    """Trenitalia result parser Class"""

    COMFORTS = ["STANDARD", "PREMIUM", "BUSINESS SALOTTINO",
                "BUSINESS AREA SILENZIO", "BUSINESS", "EXECUTIVE"]

    def __init__(self, config):
        self._result = list()
        self._searcher = TrenitaliaSearch()
        self._config = config
        if "time" not in self._config:
            self._config["time"] = "00"

    def find_page(self):
        """Returns only the first result page

        Returns:
            A list of dicts. Each element of the list represents a train
            solution and has the following structure:
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
                            }, {
                                'comfort': 'PREMIUM',
                                'price': '50.00'
                            },
                            ...
                            ...
                        ]
                    }, {
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
        html = self._searcher.get_page(self._config)
        self._parse_page(html)
        return self._result

    def find_all(self):
        """Returns all result pages"""
        # TODO
        # html = self._searcher.get_page(self._config)
        # self._parse_page(html)
        # while self._searcher.get_next():
        #     self._parse_page(html)
        return self._result

    def _parse_page(self, html):
        """Parse Trenitalia result page html"""
        soup = BeautifulSoup(html)

        # result table
        table = soup.find("table", class_="searchResult")
        if not table:
            return

        for res_tr in table.find_all("tr"):
            if not ("id" in res_tr.attrs and res_tr["id"].startswith("trow")):
                continue
            tds = res_tr.find_all("td")

            # this could occur when the solution is not availble. i.e. when
            # you search a train in the past
            if len(tds) < 6:
                continue

            dep_td = tds[0]    # departure
            arr_td = tds[1]    # arrival
            dur_td = tds[2]    # duration
            train_td = tds[3]  # train code
            price_td = tds[5]  # min price

            # this is a solution with changes
            if "rowspan" in dur_td.attrs and int(dur_td.attrs["rowspan"]) > 1:
                continue

            opt = dict()
            tmp = re.sub(r'[\t\n]*', '', train_td.div.span.getText()).split()

            # TODO: different train types have a different structure
            # at the moment parse only FRECCIAROSSA trains
            if tmp[0] != "FRECCIAROSSA":
                continue

            opt["trainType"] = tmp[0]

            # departure time is in the following day, we can exit the loop.
            if dep_td.span.string.endswith("*"):
                break

            opt["depTime"] = dep_td.span.string
            opt["arrTime"] = arr_td.span.string
            opt["duration"] = dur_td.span.string
            opt["trainCode"] = tmp[1]

            # if the train code is specified in the config dictionary, then we
            # keep only that train
            if "code" in self._config and opt["trainCode"] != self._config["code"]:
                continue;

            opt["minPrice"] = float(re.sub(r'[\s]', '',
                                    price_td.span.get_text())[:-1])
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
                    for i in range(1, len(self.COMFORTS) + 1):
                        if not tds[i].span:
                            tmp = "N/A"
                        else:
                            tmp = re.sub(r'[\s]', '', tds[i].span.get_text())
                            if tmp == "SoldOut":
                                tmp = "N/A"
                            else:
                                tmp = float(tmp[:-1])
                        pr_res["farePrices"].append({
                                                "comfort": self.COMFORTS[i-1],
                                                "price": tmp})

                    opt["prices"].append(pr_res)
                break
            self._result.append(opt)
