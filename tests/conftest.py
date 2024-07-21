import glob
import shutil
import uuid
from pathlib import Path
from typing import Callable, Generator

import pytest


@pytest.fixture(scope="module")
def search_filepath_list() -> list:
    here = Path(__file__).parent
    pattern = str(here / "data" / "results" / "*.json")
    filepath_list = [filepath for filepath in glob.glob(pattern)]
    return filepath_list


@pytest.fixture
def out_func_hoge_piyo() -> tuple[str, Callable[dict[str, int], int]]:
    def _func_hoge_piyo(result: dict) -> int:
        return result["hoge"] + result["piyo"]

    return ("hoge+piyo", _func_hoge_piyo)


@pytest.fixture
def tmp_dir() -> Generator[Path, None, None]:
    """
    一時的なディレクトリを作成し、テスト後にそのディレクトリを削除する
    """
    test_work_dir = Path() / str(uuid.uuid4())
    Path(test_work_dir).mkdir(parents=True, exist_ok=True)
    yield test_work_dir
    shutil.rmtree(test_work_dir)
