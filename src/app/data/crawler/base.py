from abc import ABC, abstractmethod
from typing import List, Dict
import os
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from app.utils.logging_utils import get_logger


class BaseCrawler(ABC):
    def __init__(self, output_dir: str = 'test_files') -> None: #`test_files`is temporary data store 
        self.output_dir = output_dir
        self.logger = get_logger(self.__class__.__name__)
        self._setup_driver()

    def _setup_driver(self) -> None:
        """Initialize Selenium Driver with default options"""
        try:
            options = Options()
            options.add_argument("--headless=new")
            self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            self.logger.error("webdriver_initialization_failed", error=str(e))
            raise

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    #Refactor with generic logging class
    def _log_download_error(self, error: Exception, url: str, filename: str = None, error_type: str = "unexpected_error") -> None:
        self.logger.error("download_failed",
                              url=url,
                              filename=filename,
                              error=str(error),
                              error_type=error_type)
    
    def cleanup(self) -> None:
        if hasattr(self, 'driver'):
            try:
                self.driver.quit()
                self.logger.info("webdriver_cleanup", status="success")
            except Exception as e:
                self.logger.error("webdriver_cleanup_failed", error=str(e))

    @abstractmethod
    def parse_page(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        pass

    def download_file(self, url: str, filename: str) -> bool:
        try:
            os.makedirs(self.output_dir, exist_ok=True)

            self.logger.info("download_started",
                             url=url,
                             filename=filename,
                             output_dir=self.output_dir)

            response = requests.get(url, stream=True)
            response.raise_for_status()

            output_path = os.path.join(self.output_dir, filename)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.logger.info("download_completed",
                            url=url,
                            filename=filename,
                            path=output_path,
                            status="success")
            
            return True
        
        except requests.exception.RequestException as e:
            self._log_download_error(e, url, filename, "request_error")
            return False
        
        except IOError as e:
            self._log_download_error(e, url, filename, "io_error")
            return False
        
        except Exception as e:
            self._log_download_error(e, url, filename)
            return False
        
    def get_page_content(self, url: str) -> BeautifulSoup:
        try:
            self.logger.info("fetching_page", url=url)
            self.driver.get(url)
            self.driver.implicitly_wait(2)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            self.logger.info("page_fetched", url=url, status="success")
            return soup
        except Exception as e:
            self.logger.error("page_fetch_failed",
                              url=url,
                              error=str(e))
            raise
