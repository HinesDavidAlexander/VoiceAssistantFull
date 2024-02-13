

def dict_to_pretty_string(input_dict: dict) -> str:
    """Prettify any dictionary into a human-readable string.

    Args:
        input_dict (dict): any input dictionary

    Returns:
        str: pretty string representation of the input dictionary
    """
    pretty_string = ""

    for key, value in input_dict.items():
        if value is not None:  # Only include entries where the value is not None
            # Capitalize the first letter and replace underscores with spaces
            formatted_key = key.replace('_', ' ').capitalize()
            pretty_string += f"{formatted_key}: {value}\n"

    return pretty_string.rstrip()  # Remove the last newline character
