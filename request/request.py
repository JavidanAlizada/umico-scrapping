import requests


class Request:

    def __init__(self, url: str = None):
        self.__url = url
        pass

    def set(self, url):
        self.__url = url

    def request(self):
        response = requests.get(self.__url)
        return response
