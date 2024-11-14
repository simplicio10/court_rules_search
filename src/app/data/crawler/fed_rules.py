from typing import Any

from bs4 import BeautifulSoup

from .base import BaseCrawler


class FederalRulesCrawler(BaseCrawler):
    def _parse_page_impl(self, soup: BeautifulSoup) -> list[dict[str, str]]:
        links = soup.find("div", class_="content")
        pdf_links = links.find_all("a", class_="download-link")

        documents = []

        for html in pdf_links:
            href = html.get("href")
            rules_name = self.strip_html(html)
            filename = self.create_filename(rules_name)

            documents.append({"url": href, "filename": filename})

        return documents

    @staticmethod
    def strip_html(html_text: Any) -> Any:
        icon = html_text.find("i")
        if icon:
            icon.decompose()

        file_info = html_text.find("span", class_="file-info")
        if file_info:
            file_info.decompose()

        cleaned_text = html_text.get_text().strip()

        return cleaned_text

    @staticmethod
    def create_filename(text: str) -> str:
        return f"{text.lower().replace(' ', '_')}.pdf"
