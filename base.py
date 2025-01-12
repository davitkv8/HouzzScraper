"""Module containing shared functionality around modules."""

import requests
from requests import exceptions as requests_exceptions

import logging

def setup_logger():
    # Create a logger
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("scrapper.log")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()

class WebPageFetcher:

    HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,ka;q=0.8",
        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    def get_source_page(self, url: str, params: dict | None = None) -> requests.Response:
        """Get requested source page."""
        try:

            if params is None:
                response = requests.get(url, headers=self.HEADERS)
            else:
                response = requests.get(url, headers=self.HEADERS, params=params)

            response.raise_for_status()

            logger.info(f"Successfully fetched {url}")

            return response

        except requests.exceptions.HTTPError as timeout_err:
            pass

        except requests_exceptions.Timeout as http_err:
            pass

        except requests_exceptions.ConnectionError as conn_err:
            pass

        except ValueError as value_err:
            pass

        except Exception as exc:
            pass

        finally:
            pass
