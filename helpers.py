"""Module containing some helper methods."""


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
