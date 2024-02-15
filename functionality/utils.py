import csv
import json

def save_json_to_csv(json_data, csv_file_path):
    """
    Converts and saves a JSON object to a CSV file.

    :param json_data: The JSON data to be saved.
    :param csv_file_path: The file path for the output CSV.
    """
    # Assuming json_data is a list of dictionaries
    with open(csv_file_path, mode='a', newline='') as file:
        if json_data:  # Check if json_data is not empty
            writer = csv.DictWriter(file, fieldnames=json_data[0].keys())
            for row in json_data:
                # Strip string values in the dictionary
                stripped_row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                writer.writerow(stripped_row)

def read_csv_to_json(csv_file_path):
    """
    Reads a CSV file and converts it into a JSON object.

    :param csv_file_path: The file path for the CSV to be read.
    :return: A list of dictionaries representing the JSON object.
    """
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        return [row for row in reader]