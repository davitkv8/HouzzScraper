"""Module implements crawling logic to get detailed view page urls for requested resources."""
import random
import re

import requests

from requests import exceptions as requests_exceptions

from bs4.element import Tag
from bs4 import BeautifulSoup
from typing_extensions import TypedDict

import models as dto_models


PAGE_URL = "https://www.houzz.com/professionals/general-contractors/aya-homes-llc-pfvwus-pf~406143371"

class MetaDataIdentifiers(TypedDict):
    """Metadata identifier details."""

    pro_id: str | None
    user_id: str | None


class HouzzCrawler:
    """Crawl detailed view page urls for requested resources."""

    COMMON_CHUNK_TYPE_PAIRS = {
        "Verified License": bool,
        "Responds Quickly": bool,
        "Pay Online": bool,
        "Hires on Houzz": int,
        "Verified Hire": int,
        "Reviews": int,
    }

    def __init__(self, url):
        self.url = url

    def _get_source_page(self):
        """Get requested source page."""

        try:
            headers = {
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
            response = requests.get(self.url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            return soup

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

    def _process_chunks(self, chunks: list[str]) -> tuple[str]:
        """Processing common chunks."""
        default_chunk_values_pair = {
            "Verified License": False,
            "Responds Quickly": False,
            "Pay Online": False,
            "Hires on Houzz": None,
            "Verified Hire": None,
            "Reviews": 0,
        }

        for common_chunk, chunk_type in self.COMMON_CHUNK_TYPE_PAIRS.items():
            match = next((s for s in chunks if common_chunk in s), None)

            if match:
                chunks.remove(match)
                if chunk_type is bool:
                    value = True

                if chunk_type is int:
                    value = int(re.search(r'\d+', match).group())

                default_chunk_values_pair[common_chunk] = value

        return *default_chunk_values_pair.values(), *chunks


    def _extract_metadata_from_header(self, content_header: Tag) -> MetaDataIdentifiers:
        """Extract metadata from header."""

        action_buttons_div = content_header.find('div', attrs={'data-container': 'Pro Actions'})
        share_button = action_buttons_div.find('button')
        pro_id = share_button.attrs.get('data-entity-id')
        user_id = content_header.attrs.get('pro_user_id')

        return {
            "pro_id": pro_id,
            "user_id": user_id,
        }


    def _extract_reviewers_data(self, metadata_identifiers: MetaDataIdentifiers):
        pass


    def _process_page(self, soup: BeautifulSoup) -> dto_models.Property | None:
        """Process detailed view page urls."""

        try:
            main_content = soup.find('main')
            if not main_content:
                pass

            content_header = main_content.find('header')

            # Get the first element inside the <header>
            info_header_divs = content_header.contents[0].contents
            company_logo = info_header_divs[0].find('img').attrs['src']
            header_metadata = self._extract_metadata_from_header(content_header)

            info = self._process_chunks(list(info_header_divs[1].stripped_strings))
            rating = 0
            if info.__len__() == 8:
                is_verified, responds_quickly, pay_online, hires_on_houzz, verified_hires, total_reviews, title, category = info
            else:
                is_verified, responds_quickly, pay_online, hires_on_houzz, verified_hires, total_reviews, title, _, rating, category, *_ = info

            business_details_section = soup.find('section', id='business')
            details = list(business_details_section.contents[1])

            property_details = {}
            for detail in details:
                field = detail.contents[0].get_text()
                value = detail.contents[1].get_text(separator=' ', strip=True)

                property_details[field] = value

            property_details_dto = dto_models.PropertyDetails(**property_details)

            review_details_section = main_content.find('section', id='reviews')
            reviews_wrapper = review_details_section.find('div', class_='reviews-wrapper')
            reviews_summary = reviews_wrapper.find_all('div', attrs={'class': 'aspect-review-summary'}) if reviews_wrapper else []

            property_reviews = {}
            for review_summary in reviews_summary:
                field = review_summary.contents[0].get_text()
                value = review_summary.contents[2].get_text()

                property_reviews[field] = value

            review_items = reviews_wrapper.find_all('div', class_='review-item') if reviews_wrapper else []
            property_reviews["reviewers"] = []
            for review_item in review_items:
                review_detail = {}

                reviewer_div = review_item.find('div', class_='review-item__reviewer')
                thumbnail_div = reviewer_div.find('div', 'review-item__reviewer_left_side')
                personal_info_div = reviewer_div.find('div', 'review-item__reviewer_right_side')

                reviewer_details = personal_info_div.find('a')

                reviewer_profile_url = reviewer_details["href"]
                reviewer_username = reviewer_details.get_text()
                reviewer_profile_img = thumbnail_div.find('a')["href"]
                submitted_review_score = personal_info_div.find('span', class_='review-rating').contents.__len__() - 1
                reviewer_comment = review_item.find('div', class_='review-item__body-string').get_text()

                review_detail["profile_url"] = reviewer_profile_url
                review_detail["full_name"] = reviewer_username
                review_detail["profile_img"] = reviewer_profile_img
                review_detail["submitted_score"] = submitted_review_score
                review_detail["comment"] = reviewer_comment

                reviewer_dto = dto_models.Reviewer(**review_detail)
                property_reviews["reviewers"].append(reviewer_dto)

            try:
                property_reviews_dto = dto_models.PropertyReviews(**property_reviews)

            except Exception as exception:
                print(exception)

            property_dto = dto_models.Property(
                title=title,
                rating=rating,
                total_reviews=total_reviews,
                category=category,
                company_logo=company_logo,
                property_reviews=property_reviews_dto,
                property_details=property_details_dto,
            )

            with open("result.json", "w") as json_file:
                json_file.write(property_dto.model_dump_json(indent=4))

            return property_dto

        except Exception as e:
            print(e)

    def run_scraper(self):
        soup = self._get_source_page()
        data = self._process_page(soup)
        print("DATA FETCHED")
        print(data.model_dump_json(indent=4))


HouzzCrawler(url=PAGE_URL).run_scraper()

