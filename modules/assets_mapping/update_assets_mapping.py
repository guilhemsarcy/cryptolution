"""Script for scrapping explicit names from raw currency codes."""
import json

import requests
from bs4 import BeautifulSoup


def update_assets_mapping() -> dict:
    """
    Scrap investing.com and get labels associated to currency symbols.

    :return: a mapping between currency code and label
    """
    res = requests.get("https://www.investing.com/crypto/currencies")

    soup = BeautifulSoup(res.text, "html.parser")
    data = soup.find_all('tr')
    cryptos = []

    for crypto in data[1:]:  # skip the header
        cryptos.append(
            {
                "symbol": crypto.find(class_="left noWrap elp symb js-currency-symbol")["title"],
                "name": crypto.find(class_="left bold elp name cryptoName first js-currency-name")["title"]
            }
        )

    return {
        item['symbol']: item['name']
        for item in cryptos
    }


if __name__ == '__main__':
    mapping = update_assets_mapping()
    with open('mapping.json', 'w') as jsn:
        json.dump(mapping, jsn, sort_keys=True, indent=4)
