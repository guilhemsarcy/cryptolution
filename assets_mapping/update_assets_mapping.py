"""Script for scrapping explicit names from raw currency codes."""
import json

import requests
from bs4 import BeautifulSoup


def update_assets_mapping():
    """
    Scrap coinmarketcap.com and get labels associated to currency codes.

    :return: a mapping between currency code and label
    :rtype: Dict
    """
    res = requests.get("https://coinmarketcap.com/all/views/all/")
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find_all('table')[2]

    rows = list()
    for row in table.findAll("tr")[1:]:
        rows.append(row)

    mp = {}
    for r in rows:
        value = r.find_all('td')
        mp[value[2].text] = value[1].text

    # tweaks
    mp['TBTC'] = 'Bitcoin'
    mp['XBT'] = 'Bitcoin'
    mp['REPV2'] = mp['REP']
    del mp['REP']
    mp['XDG'] = mp['DOGE']
    del mp['DOGE']
    mp['MLN'] = 'Melon'
    mp['PAXG'] = 'Pax gold'
    return mp


if __name__ == '__main__':
    mapping = update_assets_mapping()
    with open('mapping.json', 'w') as jsn:
        json.dump(mapping, jsn, sort_keys=True, indent=4)
