"""Tests for utils"""

import pytest

from modules.models.exceptions import FileTypeNotHandled
from modules.models.utils import read_csv_as_df


class TestReadCsv:

    def test_path_does_not_relate_to_a_csv(self):
        path = 's3://foo/bar/data.cmd'

        with pytest.raises(FileTypeNotHandled):
            read_csv_as_df(path=path)
