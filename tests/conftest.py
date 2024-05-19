import pytest
import pandas as pd
from pathlib import Path
import glob
from typing import Callable

@pytest.fixture(scope='module')
def search_filepath_list() -> list:
    here = Path(__file__).parent
    pattern = str(here / 'data' / 'results' / '*.json')
    filepath_list = [filepath for filepath in glob.glob(pattern)]
    return filepath_list


@pytest.fixture
def out_func_hoge_piyo() -> tuple[str, Callable[dict, int]]:
    def _func_hoge_piyo(result: dict) -> int:
        return result['hoge'] + result['piyo']
    return ('hoge+piyo', _func_hoge_piyo)
