"""Main file for executing data."""
from bs4 import BeautifulSoup

from base import WebPageFetcher
from crawler import HouzzSourcesCrawler


class HouzzScraper(WebPageFetcher):
    """Scraper for Houzz website."""

    def __init__(self, url: str, total_pages: int = 10):
        self.url = url
        self.total_pages = total_pages
        self.current_page = 0

        super().__init__()


    def _next_page(self):
        self.current_page += 1
        self.url = f"{self.url}?fi={self.current_page * 15}"

    def run_scraper(self):

        while self.current_page < self.total_pages:
            response = self.get_source_page(self.url)
            soup = BeautifulSoup(response.content, "html.parser")
            crawler = HouzzSourcesCrawler().process_soup(soup=soup)
            crawler.process_soup(soup)

            self._next_page()


if __name__ == '__main__':
    # url = input('Enter Houzz page URL: ')
    # total_pages = int(input('Enter total pages to scrap: '))

    page_url = "https://www.houzz.com/professionals/general-contractor/san-francisco-ca-us-probr0-bo~t_11786~r_5391959"
    total_pages_to_scrap = 1

    HouzzScraper(url=page_url, total_pages=total_pages_to_scrap).run_scraper()
