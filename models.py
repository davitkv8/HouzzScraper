"""Module to describe Pydantic dto models."""

import re

from typing import Any

from decimal import Decimal

from pydantic import BaseModel, model_validator, field_validator


__all__ = [
    "PropertyDetails",
    "Reviewer",
    "PropertyReviews",
    "Property",
]


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

    profile_url: str
    profile_img: str
    full_name: str
    submitted_score: Decimal
    comment: str

class PropertyReviews(BasePropertyDTO):
    """Defines common attributes for reviews dto details."""

    communication: Decimal | None = None
    value: Decimal | None = None
    work_quality: Decimal | None = None
    reviewers: list[Reviewer]


class Property(BasePropertyDTO):
    """Defines common details for top-level Property dto."""

    title: str
    category: str
    company_logo: str | None = None
    rating: Decimal
    total_reviews: int

    property_details: PropertyDetails
    property_reviews: PropertyReviews
