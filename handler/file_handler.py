import json
import os


class FileHandler:
    def __init__(self, data=None, json_file=None):
        self.__data = data
        self.__json_file = json_file

    def set_data(self, data):
        self.__data = data
        return self

    def set_json_file(self, json_file):
        self.__json_file = json_file
        return self

    def __generate_dir_if_not_exists(self):
        directory = os.path.dirname(self.__json_file)
        os.makedirs(directory, exist_ok=True)

    def write_to_json_file(self):
        print(f"Writing to {self.__json_file} File ...")
        self.__generate_dir_if_not_exists()
        with open(self.__json_file, 'w+', encoding='utf-8') as json_file:
            json.dump(self.__data, json_file, indent=4, ensure_ascii=False)

    def read_from_file(self):
        print(f"Reading From {self.__json_file} File ...")
        with open(self.__json_file, "r", encoding="utf-8") as file:
            data_dict = json.load(file)
        return data_dict

    def clear_file(self):
        if os.path.isfile(self.__json_file):
            with open(self.__json_file, "w") as file:
                file.truncate()
        else:
            print("File does not exist.")
