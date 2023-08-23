import json
from os import makedirs, path

def load_data_from_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def save_data_to_json(filename, data):
    # Check if the directory exists and create it if not
    directory = path.dirname(filename)
    if directory and not path.exists(directory):
        makedirs(directory)

    # Save the data to the file
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)