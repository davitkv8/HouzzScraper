import requests
from pprint import pprint

url = "https://www.houzz.com/j/ajax/profileReviewsAjax"

params = {
    "userId": "54723411",
    "proId": "2455499",
    "fromItem": "0",
    "itemsPerPage": "1024",
    "sortType": "NEWEST",
    "searchWord": "",
    "isPrivateView": "undefined",
}

def get_nested_key(data, target_key):
    """
    Recursively searches for a key in a nested dictionary and returns its value.

    :param data: Dictionary to search in.
    :param target_key: Key to find in the dictionary.
    :return: The value of the target key if found, otherwise None.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            # Recursively search in the value if it's a dictionary or list
            nested_result = get_nested_key(value, target_key)
            if nested_result is not None:
                return nested_result
    elif isinstance(data, list):
        for item in data:
            nested_result = get_nested_key(item, target_key)
            if nested_result is not None:
                return nested_result
    return None


# Headers copied from the browser
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

# Make the GET request
response = requests.get(url, headers=headers, params=params)

data = response.json()

reviews = get_nested_key(data, "ProfessionalReviewsStore").get("data")
users = get_nested_key(data, "UserStore").get("data")

reviews_mapped_by_user_id = {}
for review in reviews.values():

    reviewer_user_id = review["userId"]
    user = users[str(reviewer_user_id)]

    reviewer_dto = {
        "display_name": user.get("displayName"),
        "is_professional": user.get("isProfessional"),
        "profile_image": user.get("profileImage"),
    }

    review_dto = {
        "reviewer": reviewer_dto,
        "comment": review["body"],
        "relationship_type": review["relationship"],
        "project_date": review["projectDate"],
        "project_price": review["projectPrice"],
        "project_price_as_string": review["projectPriceAsString"],
        "submitted_rating": review["rating"],
        "status": review["status"],
        "created_at": review["created"],
        "updated_at": review["modified"],
        "total_likes": review["numberOfLikes"],
        "is_liked": review["isLiked"],
    }

    reviews_mapped_by_user_id[review["userId"]] = review_dto

print(reviews_mapped_by_user_id)
