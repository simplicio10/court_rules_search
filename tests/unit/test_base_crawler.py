from collections.abc import Generator

import pytest
from app.data.crawler.base import BaseCrawler
from bs4 import BeautifulSoup


class TestCrawler(BaseCrawler):
    def _parse_page_impl(self, soup: BeautifulSoup) -> list[dict[str, str]]:
        return [{"title": "Test Document", "url": "http://test.com"}]


"""@pytest.fixture
def mock_driver() -> Generator:
    with patch("selenium.webdriver.Chrome") as mock:
        driver_instance = Mock()
        driver_instance.session_id = "test_session"
        driver_instance.capabilities = {"browserVersion": "test_version"}
        mock.return_value = driver_instance
        yield mock"""


@pytest.fixture
def crawler() -> Generator[TestCrawler, None, None]:
    with TestCrawler(output_dir="test_output") as c:
        yield c


class TestBaseCrawler:
    def test_initialization(self, crawler: TestCrawler) -> None:
        assert crawler.output_dir == "test_output"
        assert crawler.driver is not None
