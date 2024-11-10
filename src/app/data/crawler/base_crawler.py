from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import requests
from datetime import datetime

url = "https://www.uscourts.gov/rules-policies/current-rules-practice-procedure"

def download_pdf(pdf_link: str, file_url: str, output_dir: str='test_files') -> None:
    os.makedirs(output_dir, exist_ok=True)

    filename = ' '.join(pdf_link.strip())

def strip_html(html_text: None) -> str:
    icon = html_text.find('i')
    if icon:
        icon.decompose()
    
    file_info = html_text.find('span', class_='file-info')
    if file_info:
        file_info.decompose()

    cleaned_text = html_text.get_text().strip()

    return cleaned_text

def create_filename(text: str) -> str:
    filename = text.lower().replace(' ', '_')
    return f"{filename}.pdf"

def download_fed_rules(url: str) -> None:
    #Refactor - Create driver class
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    driver.get(url)

    driver.implicitly_wait(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    links = soup.find('div', class_='content')
    pdf_links = links.find_all('a', class_='download-link')

    for html in pdf_links:
        href = soup.get('href')
        full_url = f'{url}{href}'

        rules_name = strip_html(html)
        filename = create_filename(rules_name)

        print(filename)

        


if __name__ == "__main__":
    download_fed_rules(url)