def process_docstring_alt(docstring): # Unused
    """
    Processes a function's docstring to strip out everything after "Args:" or "Returns:",
    or just strips blank space if neither are there.

    Parameters:
    - docstring: The docstring of a function.

    Returns:
    The processed docstring.
    """
    if "Args:" in docstring:
        if "Returns:" in docstring:
            docstring = docstring.split("Returns:")[0].strip()
        args = docstring.split("Args:")[1].strip()
        return "Args: " + args
    else:
        return ""

def process_docstring(docstring: str) -> str:
    """Converts a raw docstring into a processed docstring more conducive to consistent LLM responses.

    Args:
        docstring (str): raw docstring

    Returns:
        str: processed docstring
    """
    docstring = docstring.replace("\n", " ").strip()
    if "Returns:" in docstring:
        return docstring.split("Returns:")[0].strip()

def replace_callables_with_docstrings(d):
    """
    Recursively traverses a dictionary, creating a new dictionary where any callable item is replaced with its docstring.
    
    :param d: The dictionary to process, which may contain nested dictionaries and callables.
    :return: A new dictionary with callables replaced by their docstrings.
    """
    new_dict = {}
    for key, value in d.items():
        if callable(value):
            # Replace the callable with its docstring, or with an empty string if it has no docstring
            docstring = value.__doc__ if value.__doc__ else ''
            new_dict[key] = process_docstring(docstring) if docstring else value.__name__
        elif isinstance(value, dict):
            # Recursively process nested dictionaries and assign the returned new dictionary
            new_dict[key] = replace_callables_with_docstrings(value)
        else:
            # For non-callable, non-dictionary items, just copy them to the new dictionary
            new_dict[key] = value
    return new_dict

# def dict_functions_to_string(input_dict, indent_level=0):
#     """
#     Recursively converts a dictionary with functions or nested dictionaries as values
#     into a string. For functions, it uses a processed description (docstring) that strips out
#     everything after "Args:" or "Returns:", or just blank space if neither are there. For nested
#     dictionaries, it recursively processes each nested level.

#     Parameters:
#     - input_dict: A dictionary where the values can be functions or other dictionaries.
#     - indent_level: The current level of indentation, used for formatting nested dictionaries.

#     Returns:
#     A string representation of the dictionary, with clear indication of nested structures.
#     """
#     lines = []
#     indent = "    " * indent_level  # Indentation for readability

#     for key, value in input_dict.items():
#         if callable(value):  # Check if the value is a function
#             docstring = value.__doc__ if value.__doc__ else ""
#             description = process_docstring(docstring) if docstring else value.__name__
#             line = f"{indent}{key}: {description}"
#         elif isinstance(value, dict):  # Check if the value is a nested dictionary
#             nested_lines = dict_functions_to_string(value, indent_level + 1)
#             line = f"{indent}{key}:\n{nested_lines}"
#         else:
#             line = f"{indent}{key}: {value}"

#         lines.append(line)

#     return "\n".join(lines)

