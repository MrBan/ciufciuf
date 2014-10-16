"""Trenitalia Service Module"""

from TrenitaliaSearch import TrenitaliaSearch
from bs4 import BeautifulSoup
import re

class TrenitaliaParser(object):
    """Trenitalia result parser Class"""

    COMFORTS = ["STANDARD", "PREMIUM", "BUSINESS SALOTTINO",
                "BUSINESS AREA SILENZIO", "BUSINESS", "EXECUTIVE"]

    def __init__(self):
        self._result = list()
        self._searcher = TrenitaliaSearch()

    def find_page(self, config):
        """Returns only the first result page"""
        html = self._searcher.get_page(config)
        self._parse_page(html)
        return self._result

    def find_all(self, config):
        """Returns all result pages"""
        # TODO
        # html = self._searcher.get_page(config)
        # self._parse_page(html)
        # while self._searcher.get_next():
        #     self._parse_page(html)
        return self._result

    def _parse_page(self, html):
        """Parse Trenitalia result page html

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
        soup = BeautifulSoup(html)

        # result table
        table = soup.find("table", class_="searchResult")
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

            # departure time is in the following day
            if dep_td.span.string.endswith("*"):
                break

            opt["depTime"] = dep_td.span.string
            opt["arrTime"] = arr_td.span.string
            opt["duration"] = dur_td.span.string
            opt["trainCode"] = tmp[1]
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
