from abc import ABC, abstractmethod
from typing import List, Dict
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from app.utils.logging_utils import LoggingMixin


class BaseCrawler(ABC, LoggingMixin):
    def __init__(self, output_dir: str = 'test_files') -> None: #`test_files`is temporary data store 
        super().__init__() #Initializes logging
        self.output_dir = output_dir
        self._setup_driver()

    def _setup_driver(self) -> None:
        """Initialize Selenium Driver with default options"""
        with self._log_operation("webdriver_initialization") as log:
            options = Options()
            options.add_argument("--headless=new")
            self.driver = webdriver.Chrome(options=options)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def cleanup(self) -> None:
        if hasattr(self, 'driver'):
            with self._log_operation("webdriver_cleanup") as log:
                log.update({
                    "session_id": getattr(self.driver.session_id),
                    "had_session": hasattr(self.driver, "session_id")})
                self.driver.quit()
                
                self.driver = None

    def parse_page(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        with self._log_operation("page_parse") as log:
            documents = self._parse_page_impl(soup)
            log.update({"document_count": len(documents)})
            return documents
    
    @abstractmethod
    def _parse_page_impl(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        pass

    def download_file(self, url: str, filename: str) -> bool:
        with self._log_operation("download") as log:
            log.update({
                "url": url,
                "filename": filename,
                "output_dir": self.output_dir
            })

            os.makedirs(self.output_dir, exist_ok=True)

            response = requests.get(url, stream=True)
            response.raise_for_status()

            output_path = os.path.join(self.output_dir, filename)
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            log.update({"path": output_path})
            
            return True
        
    def get_page_content(self, url: str) -> BeautifulSoup:
        with self._log_operation("page_fetch") as log:
            log.update({"url": url})
            self.driver.get(url)
            self.driver.implicitly_wait(2)
            return BeautifulSoup(self.driver.page_source, 'html.parser')
