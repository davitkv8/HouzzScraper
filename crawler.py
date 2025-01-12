"""Module implements crawling logic to get detailed view page urls for requested resources."""
import time

from tasks import parse_page_task


class HouzzSourcesCrawler:
    """Crawl detailed view page urls for requested resources."""

    @staticmethod
    def process_soup(soup):
        search_result_div = soup.find('div', class_='pro-results')
        if search_result_div is None:
            pass

        result_list = search_result_div.find('ul', class_='hz-pro-search-results')
        if result_list is None:
            pass

        a_tags = result_list.select('li > a')
        if result_list is None:
            pass

        for a_tag in a_tags:
            href = a_tag['href']
            parse_page_task.delay(href)
            time.sleep(0.5)
