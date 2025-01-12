"""Module implements crawling logic to get detailed view page urls for requested resources."""
import json
import time
import threading

from queue import Queue
from tasks import parse_page_task


class HouzzSourcesCrawler:
    """Crawl detailed view page urls for requested resources."""

    RESULT_QUEUE = Queue()
    SIGNAL = threading.Event()

    def process_soup(self, soup):
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
            result = parse_page_task.delay(href)
            self.RESULT_QUEUE.put(result)

        # All tasks have been submitted
        self.SIGNAL.set()

    def monitor_tasks(self):
        """
        Function to monitor task completion.
        Continuously checks the queue for AsyncResult objects and processes them.
        Exits when the queue is empty and submission is done.
        """
        while not (self.SIGNAL.is_set() and self.RESULT_QUEUE.empty()):
            if not self.RESULT_QUEUE.empty():
                result = self.RESULT_QUEUE.get()
                while not result.ready():
                    time.sleep(1)

                # Task is ready, process the result
                with open("results.jsonl", "a") as file:
                    json.dump(json.loads(result.result), file)
                    file.write("\n")
            else:
                time.sleep(1)  # Just avoiding bust waiting here

    def run(self, soup):
        """Main process."""
        submit_thread = threading.Thread(target=self.process_soup, args=(soup, ))
        monitor_thread = threading.Thread(target=self.monitor_tasks)

        # Start threads
        submit_thread.start()
        monitor_thread.start()

        # Wait for threads to complete
        submit_thread.join()
        monitor_thread.join()
        print(f"All tasks monitored and completed. Scrapped data - results.jsonl\nApp Logs - app.log")
