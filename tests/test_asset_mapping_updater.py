import pytest

from modules.assets_mapping.update_assets_mapping import AssetMappingUpdater
from modules.models.exceptions import UnknownURLError, WrongFormatForHTML, NotExistingHTMLClass

from bs4 import BeautifulSoup

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

    def test_soupify_wrong_html(self, asset_mapping_updater):
        asset_mapping_updater.html = 'wrong html'
        with pytest.raises(WrongFormatForHTML):
            asset_mapping_updater.soupify_html()

    def test_soupify_good_html(self, asset_mapping_updater):
        asset_mapping_updater.html = '<a class="a">good html</a>'
        asset_mapping_updater.soupify_html()
        assert asset_mapping_updater.soup.text == 'good html'

    @staticmethod
    def test_find_from_soup_not_existing_class():
        with pytest.raises(NotExistingHTMLClass):
            AssetMappingUpdater.find_from_soup(
                elem=BeautifulSoup('<a class="a"> html </a>', 'html.parser'),
                elem_class='b'
            )
