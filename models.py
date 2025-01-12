"""Module to describe Pydantic dto models."""

import re

import datetime as dt

from typing import Any

from decimal import Decimal

from pydantic import BaseModel, model_validator, field_validator


__all__ = [
    "PropertyDetails",
    "Reviewer",
    "ReviewCard",
    "PropertyReviews",
    "Property",
]

from base import logger


class BasePropertyDTO(BaseModel):
    """Base configuration class for property dtos"""

    class Config:
        extra = "ignore"

    @model_validator(mode='before')
    @classmethod
    def pre_validate_all_fields(cls, data: Any) -> Any:
        """Validate all fields before they are created."""

        result = {}
        for field, value in data.items():
            cleaned_field = field.replace(" ", "_").lower()
            result[cleaned_field] = value

        return result


class PropertyDetails(BasePropertyDTO):
    """Defines common attributes for property dto details."""

    address: str | None = None
    business_name: str | None = None
    followers: str | None = None
    license_number: str | None = None
    phone_number: str | None = None
    typical_job_cost: tuple[Decimal | None, Decimal | None] | None = None
    website: str | None = None

    @field_validator('typical_job_cost', mode='before')
    @classmethod
    def validate_typical_job_cost(cls, typical_job_cost: str | None = None) -> tuple[Decimal, Decimal] | None:
        """Validate all fields before they are created."""

        if not typical_job_cost:
            return None

        parts = typical_job_cost.split('-')

        low = Decimal(re.sub(r'[^\d.]', '', parts[0]))  if parts[0].strip() else None
        high = Decimal(re.sub(r'[^\d.]', '', parts[1])) if parts[1].strip() else None

        return low, high



class Reviewer(BasePropertyDTO):
    """Defines common attributes for reviewer dto details."""

    display_name: str
    is_professional: bool = False
    profile_image: str | None = None


class ReviewCard(BasePropertyDTO):
    """Defines common attributes for review card dto details."""
    author: Reviewer
    comment: str
    relationship_type: str
    project_date: dt.date | None = None
    project_price: Decimal | None = None
    project_price_as_string: str | None = None
    submitted_rating: int | None = None
    status: str | None = None
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None
    total_likes: int | None = None
    is_liked: bool = False

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, int):
            return dt.datetime.fromtimestamp(value)

        return value

    @field_validator("project_date", mode="before")
    @classmethod
    def validate_project_date(cls, value):
        try:
            if isinstance(value, str) and value != "0000-00-00":
                return dt.date.fromisoformat(value)
        except (ValueError, TypeError):
            logger.warning("Invalid project date: '%s'", value)
        return None


class PropertyReviews(BasePropertyDTO):
    """Defines common attributes for reviews dto details."""

    communication: Decimal | None = None
    value: Decimal | None = None
    work_quality: Decimal | None = None
    reviews: list[ReviewCard]


class Property(BasePropertyDTO):
    """Defines common details for top-level Property dto."""

    title: str
    category: str
    company_logo: str | None = None
    rating: Decimal
    total_reviews: int

    property_details: PropertyDetails
    property_reviews: PropertyReviews
