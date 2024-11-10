from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import requests
from urllib.parse import urljoin

url = "https://www.uscourts.gov/rules-policies/current-rules-practice-procedure"

def download_pdf(pdf_link: str, filename: str, output_dir: str='test_files') -> None:
    print(f"Attempting {pdf_link}")
    try:
        os.makedirs(output_dir, exist_ok=True)

        response = requests.get(pdf_link, stream=True)
        response.raise_for_status()

        output_path = os.path.join(output_dir, filename)
        print(f"Saving to: {output_path}")

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return {
            'filename': filename,
            'url': pdf_link,
            'status': 'success',
            'path': output_path
        }
    except Exception as e:
        print(f"Error downloading {filename}: {str(e)}")  # Debug print
        return {
            'filename': filename,
            'url': pdf_link,
            'status': 'error',
            'error': str(e)
        }


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

    results = []

    for html in pdf_links:
        href = html.get('href')
        full_url = urljoin(url, href)

        rules_name = strip_html(html)
        print(rules_name)
        filename = create_filename(rules_name)

        result = download_pdf(full_url, filename)

        results.append(result)
        print(f"Downloaded: {filename}" if result['status'] == 'success' else 
              f"Error downloading {filename}: {result.get('error')}")


    driver.quit()
    return results

if __name__ == "__main__":
    download_fed_rules(url)