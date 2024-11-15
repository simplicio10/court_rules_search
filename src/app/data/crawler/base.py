import os
from abc import ABC, abstractmethod
from typing import Any

import requests
from app.utils.logging_utils import LoggingMixin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BaseCrawler(ABC, LoggingMixin):
    def __init__(self, output_dir: str = "test_files") -> None:
        # `test_files`is temporary data store
        super().__init__()  # Initializes logging
        self.output_dir: str = output_dir
        self.driver: webdriver.Chrome | None = None
        self._setup_driver()

    def _setup_driver(self) -> None:
        """Initialize Selenium Driver with default options"""
        with self._log_operation("webdriver_initialization") as log:
            options = Options()
            options.add_argument("--headless=new")
            self.driver = webdriver.Chrome(options=options)
            log.update(
                {
                    "headless": True,
                    "browser": "chrome",
                    "session_id": self.driver.session_id,
                    "capabilities": self.driver.capabilities.get("browserVersion", "unknown"),
                }
            )

    def __enter__(self) -> "BaseCrawler":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        self.cleanup()

    def cleanup(self) -> None:
        if self.driver is not None:
            with self._log_operation("webdriver_cleanup") as log:
                session_id = getattr(self.driver, "session_id", None)
                log.update(
                    {
                        "session_id": session_id,
                        "had_session": session_id is not None,
                    }
                )
                self.driver.quit()

                self.driver = None

    def parse_page(self, soup: BeautifulSoup) -> list[dict[str, str]]:
        with self._log_operation("page_parse") as log:
            documents = self._parse_page_impl(soup)
            log.update({"document_count": len(documents)})
            return documents

    @abstractmethod
    def _parse_page_impl(self, soup: BeautifulSoup) -> list[dict[str, str]]:
        pass

    def download_file(self, url: str, filename: str) -> bool:
        with self._log_operation("download") as log:
            log.update({"url": url, "filename": filename, "output_dir": self.output_dir})

            os.makedirs(self.output_dir, exist_ok=True)

            response = requests.get(url, stream=True)
            response.raise_for_status()

            output_path = os.path.join(self.output_dir, filename)
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            log.update({"path": output_path})

            return True

    def get_page_content(self, url: str) -> BeautifulSoup:
        if self.driver is None:
            raise RuntimeError("WebDriver not initialized")

        with self._log_operation("page_fetch") as log:
            log.update({"url": url})
            self.driver.get(url)
            self.driver.implicitly_wait(2)
            return BeautifulSoup(self.driver.page_source, "html.parser")
