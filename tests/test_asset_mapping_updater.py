import pytest
from bs4 import BeautifulSoup

from modules.assets_mapping.update_assets_mapping import AssetMappingUpdater
from modules.models.exceptions import (NotExistingHTMLClass, UnknownURLError,
                                       WrongFormatForHTML)


@pytest.fixture
def asset_mapping_updater():
    return AssetMappingUpdater(
        url='https://unknown-url-for-testing.com',
        updated_file='file.json'
    )


class TestAssetMappingUpdater:

    def test_get_html_unknown_url(self, asset_mapping_updater):
        with pytest.raises(UnknownURLError):
            asset_mapping_updater.get_html()

    def test_soupify_html(self, asset_mapping_updater):
        asset_mapping_updater.html = "<html><body><h1>Good html!</h1></body></html>"
        asset_mapping_updater.soupify_html()

        assert isinstance(asset_mapping_updater.soup, BeautifulSoup)

    def test_soupify_html_wrong_html(self, asset_mapping_updater):
        asset_mapping_updater.html = 'Wrong html!'
        with pytest.raises(WrongFormatForHTML):
            asset_mapping_updater.soupify_html()

    def test_soupify_good_html(self, asset_mapping_updater):
        asset_mapping_updater.html = '<a class="a">good html</a>'
        asset_mapping_updater.soupify_html()
        assert asset_mapping_updater.soup.text == 'good html'

    def test_build_mapping(self, asset_mapping_updater):
        soup = BeautifulSoup('''
                <table>
                    <tr>
                        <th>Symbol</th>
                        <th>Name</th>
                    </tr>
                    <tr>
                        <td class="left noWrap elp symb js-currency-symbol" title="BTC">BTC</td>
                        <td class="left bold elp name cryptoName first js-currency-name" title="Bitcoin">Bitcoin</td>
                    </tr>
                    <tr>
                        <td class="left noWrap elp symb js-currency-symbol" title="ETH">ETH</td>
                        <td class="left bold elp name cryptoName first js-currency-name" title="Ethereum">Ethereum</td>
                    </tr>
                </table>
            ''', 'html.parser')

        asset_mapping_updater.build_mapping(soup.find_all('tr'))

        expected_mapping = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum'
        }
        assert asset_mapping_updater.mapping == expected_mapping

    @staticmethod
    def test_find_from_soup_not_existing_class():
        with pytest.raises(NotExistingHTMLClass):
            AssetMappingUpdater.find_from_soup(
                elem=BeautifulSoup('<a class="a"> html </a>', 'html.parser'),
                elem_class='b'
            )
