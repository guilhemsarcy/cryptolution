"""Script for scrapping explicit names from raw currency codes."""
import json

import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet

from dataclasses import dataclass
from modules.models.exceptions import UnknownURLError, WrongFormatForHTML, NotExistingHTMLClass


@dataclass
class AssetMappingUpdater:
    """Class for updating assets mapping from scraped data."""
    url: str = None
    updated_file: str = None
    html: str = None
    soup: BeautifulSoup = None
    mapping: dict = None

    def get_html(self):
        """
        Retrieve html source code from website url.
        """
        try:
            html = requests.get(url=self.url).text
        except requests.exceptions.ConnectionError:
            raise UnknownURLError(self.url)
        self.html = html

    def soupify_html(self):
        """
        Soupify html source code.
        """
        soup = BeautifulSoup(self.html, "html.parser")
        if soup.text == self.html:
            raise WrongFormatForHTML
        self.soup = soup

    def build_mapping(self, table: ResultSet):
        """
        Build mapping from scraping.
        """
        lst = []
        for row in table[1:]:  # skip the header
            lst.append(
                {
                    "symbol": row.find(class_="left noWrap elp symb js-currency-symbol")["title"],
                    "name": row.find(class_="left bold elp name cryptoName first js-currency-name")["title"]
                }
            )

        self.mapping = {
            item['symbol']: item['name']
            for item in lst
        }

    @staticmethod
    def find_from_soup(elem: BeautifulSoup, elem_class: str) -> BeautifulSoup:
        """
        Find element from soup object.

        :param elem: html element of interest
        :param elem_class: class to look for

        :return: soup object of interest
        """
        res = elem.find(class_=elem_class)
        if res is None:
            raise NotExistingHTMLClass(elem_class)
        return res


def get_assets_mapping() -> dict:
    """
    Scrap investing.com and get labels associated to currency symbols.

    :return: a mapping between currency code and label
    """
    mapping_updater = AssetMappingUpdater(
        url="https://www.investing.com/crypto/currencies",
        updated_file="mapping.json"
    )
    mapping_updater.get_html()
    mapping_updater.soupify_html()

    data = mapping_updater.soup.find_all('tr')
    mapping_updater.build_mapping(table=data)
    return mapping_updater.mapping


if __name__ == '__main__':
    mapping = get_assets_mapping()
    with open('mapping.json', 'w') as jsn:
        json.dump(mapping, jsn, sort_keys=True, indent=4)
