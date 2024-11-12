from typing import List
from fed_rules import FederalRulesCrawler
from urllib.parse import urljoin

def main(url: str, output_dir: str = 'test_files') -> List[bool]:
    results = []
    
    with FederalRulesCrawler(output_dir=output_dir) as crawler:
        soup = crawler.get_page_content(url)
        documents = crawler.parse_page(soup)

        for doc in documents:
            full_url = urljoin(url, doc['url'])
            result = crawler.download_file(full_url, doc['filename'])
            results.append(result)
        
        return result

if __name__ == "__main__":
    url = "https://www.uscourts.gov/rules-policies/current-rules-practice-procedure"
    main(url)