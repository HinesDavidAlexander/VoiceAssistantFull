from openai import OpenAI
import os
from functionality.convert_command_dict import replace_callables_with_docstrings
import json

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI()

def read_file_content(filename):
    """
    Open a file and read its contents into a string variable.

    Args:
    filename (str): The path to the file to be read.

    Returns:
    str: The contents of the file as a string.
    """
    try:
        with open(filename, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Read in the action prompt at load time
file_content = read_file_content("functionality/prompts/action_prompt.txt")

def string_to_dict(dict_string):
    """
    Converts a string representation of a dictionary into a Python dictionary.

    Parameters:
    - dict_string: A string representation of a dictionary.

    Returns:
    A Python dictionary parsed from the input string.
    """
    try:
        result_dict = json.loads(dict_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid dictionary string: {e}")

    return result_dict

def get_action(user_message, command_dict):
    commands_str = replace_callables_with_docstrings(command_dict)
    print(f"Commands String: {commands_str}")
    final_message = "I request the action: " + user_message + ". Select from the following options: " + str(commands_str)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={ "type": "json_object" },
        messages=[
        {"role": "system", "content": file_content}, 
        {"role": "user", "content": final_message}
        ]
    )
    
    print(f"LLM Response: {response.choices[0].message.content}")
    response_dict = string_to_dict(response.choices[0].message.content)
    
    return response_dict