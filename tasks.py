"""Module containing celery tasks."""
import json
import re
from typing import TypedDict

from celery import Celery
from bs4.element import Tag
from bs4 import BeautifulSoup

from base import WebPageFetcher, logger
from helpers import get_nested_key
import models as dto_models

app = Celery(
    'houzz_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

class MetaDataIdentifiers(TypedDict):
    """Metadata identifier details."""

    userId: str | None
    proId: str | None
    fromItem: str
    itemsPerPage: str
    sortType: str
    searchWord: str
    isPrivateView: str

COMMON_CHUNK_TYPE_PAIRS = {
    "Verified License": bool,
    "Responds Quickly": bool,
    "Pay Online": bool,
    "Hires on Houzz": int,
    "Verified Hire": int,
    "Reviews": int,
}

REVIEWS_AJAX_BASE_URL = "https://www.houzz.com/j/ajax/profileReviewsAjax"


def process_chunks(chunks: list[str]) -> tuple:
    """Processing common chunks."""
    default_chunk_values_pair = {
        "Verified License": False,
        "Responds Quickly": False,
        "Pay Online": False,
        "Hires on Houzz": None,
        "Verified Hire": None,
        "Reviews": 0,
    }

    for common_chunk, chunk_type in COMMON_CHUNK_TYPE_PAIRS.items():
        match = next((s for s in chunks if common_chunk in s), None)

        if match:
            chunks.remove(match)
            value = match

            if chunk_type is bool:
                value = True

            if chunk_type is int:
                value = int(re.search(r'\d+', match).group())

            default_chunk_values_pair[common_chunk] = value

    return *default_chunk_values_pair.values(), *chunks


def extract_metadata_from_header(content_header: Tag) -> MetaDataIdentifiers:
    """Extract metadata from header."""

    action_buttons_div = content_header.find('div', attrs={'data-container': 'Pro Actions'})
    share_button = action_buttons_div.find('button')
    pro_id = share_button.attrs.get('data-entity-id')
    js_str = content_header.attrs.get('data-extra-info')
    user_id = json.loads(js_str).get("pro_user_id") if js_str else None

    return {
        "userId": user_id,
        "proId": pro_id,
        "fromItem": "0",
        "itemsPerPage": "1024",
        "sortType": "NEWEST",
        "searchWord": "",
        "isPrivateView": "undefined",
    }


@app.task(rate_limit='1/s')
def parse_page_task(url: str) -> str:
    """Process detailed view page urls."""

    page_fetcher = WebPageFetcher()
    response = page_fetcher.get_source_page(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    try:

        main_content = soup.find('main')
        if not main_content:
            pass

        content_header = soup.find('header')
        if not content_header:
            pass

        # Get the first element inside the <header>
        info_header_divs = content_header.contents[0].contents
        company_img_attrs = getattr(info_header_divs[0].find('img'), 'attrs', None)
        company_logo = company_img_attrs['src'] if company_img_attrs else None
        header_metadata = extract_metadata_from_header(content_header)

        info = process_chunks(list(info_header_divs[1].stripped_strings))
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

        review_details_section = soup.find('section', id='reviews')
        reviews_wrapper = review_details_section.find('div', class_='reviews-wrapper')
        reviews_summary = reviews_wrapper.find_all('div', attrs={'class': 'aspect-review-summary'}) if reviews_wrapper else []

        property_reviews = {}
        for review_summary in reviews_summary:
            field = review_summary.contents[0].get_text()
            value = review_summary.contents[2].get_text()

            property_reviews[field] = value

        response = page_fetcher.get_source_page(url=REVIEWS_AJAX_BASE_URL, params=header_metadata)
        data = response.json()

        reviews = get_nested_key(data, "ProfessionalReviewsStore").get("data")
        users = get_nested_key(data, "UserStore").get("data")

        review_cards: list[dto_models.ReviewCard] = []
        for review in reviews.values():
            reviewer_user_id = review["userId"]
            user = users[str(reviewer_user_id)]

            reviewer_dto = dto_models.Reviewer(
                display_name=user["displayName"],
                is_professional=user.get("isProfessional", False),
                profile_image=user.get("profileImage", None),
            )

            try:
                review_card_dto = dto_models.ReviewCard(
                    author=reviewer_dto,
                    comment=review.get("body"),
                    relationship_type=review.get("relationship"),
                    project_date=review.get("projectDate"),
                    project_price=review.get("projectPrice"),
                    project_price_as_string=review.get("projectPriceAsString"),
                    submitted_rating=review.get("rating"),
                    status=review.get("status"),
                    created_at=review.get("created"),
                    updated_at=review.get("modified"),
                    total_likes=review.get("numberOfLikes"),
                    is_liked=review.get("isLiked"),
                )
            except Exception as e:
                logger.warning("Unexpected data received for `models.ReviewCard`: %s", e)
                continue

            review_cards.append(review_card_dto)

        property_reviews["reviews"] = review_cards
        property_reviews_dto = dto_models.PropertyReviews(**property_reviews)

        property_dto = dto_models.Property(
            title=title,
            rating=rating,
            total_reviews=total_reviews,
            category=category,
            company_logo=company_logo,
            property_reviews=property_reviews_dto,
            property_details=property_details_dto,
        )

        logger.info(f"Parsed property {property_dto.model_dump_json(indent=2)}")

        return property_dto.model_dump_json(indent=2)

    except Exception as e:
        logger.warning(f"Failed to parse page: {url}: {e}")
