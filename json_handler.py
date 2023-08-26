import json
from os import makedirs, path



def load_data_from_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data_to_json(filename, data):
    # Check if the directory exists and create it if not
    directory = path.dirname(filename)
    if directory and not path.exists(directory):
        makedirs(directory)

    # Save the data to the file
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_settings()
        return cls._instance

    def _load_settings(self):
            self._settings = load_data_from_json("settings.json")["settings"]

    def get_location(self, key):
        return self._settings["locations"].get(key)

    def get_default(self, key):
        return self._settings["defaults"].get(key)

# Usage:
config = Config()