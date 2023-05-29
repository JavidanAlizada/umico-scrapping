import os

from .constants import *

# PROJECT_NAME = "umico"
GENERATED_FOLDER = "result"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_full_path(file):
    return os.path.join(BASE_DIR, GENERATED_FOLDER, file)


class FilePath:
    __UMICO_CATEGORY_AND_PRODUCT_JSON_FILE = UMICO_JSON
    __UMICO_CATEGORY_JSON_FILE = CATEGORY_JSON
    __UMICO_PRODUCT_JSON_FILE = PRODUCT_JSON
    UMICO_CATEGORY_AND_PRODUCT_JSON_FILE_FULL_PATH = _get_full_path(__UMICO_CATEGORY_AND_PRODUCT_JSON_FILE)
    UMICO_CATEGORY_JSON_FILE_FULL_PATH = _get_full_path(__UMICO_CATEGORY_JSON_FILE)
    UMICO_PRODUCT_JSON_FILE_FULL_PATH = _get_full_path(__UMICO_PRODUCT_JSON_FILE)


QUESTION_MARK = '?'
AMPERSAND_MARK = '&'
EMTPY_STRING = ''


class Endpoint:
    class Category:
        url = CATEGORY_URL
        query_params = {
            'static_params': CATEGORY_QUERY_PARAMS,
            'dynamic_params': {
                'start_node_id': ''
            }
        }

    class Product:
        url = PRODUCT_URL
        query_params = {
            'static_params': PRODUCT_STATIC_QUERY_PARAMS,
            'dynamic_params': {
                'per_page': '100',
                'page': '1',
                'q%5Bcategory_id_in%5D': '',
            }
        }

    class ProductFeatures:
        url = PRODUCT_FEATURES_URL
        query_params = {
            'static_params': PRODUCT_FEATURES_STATIC_QUERY_PARAMS,
            'dynamic_params': {
                'per_page': '100',
                'page': '1',
                'q%5Bcategory_id_in%5D': '',
            }
        }

    def __get_iterative_dynamic_params(self, query_params: dict):
        response_params = EMTPY_STRING
        dynamic_params = query_params['dynamic_params']
        for key in dynamic_params:
            response_params += f"{AMPERSAND_MARK}{key}={dynamic_params[key]}"
        response = f"{query_params['static_params']}"
        return f"{response}{response_params}" if response_params and response_params != EMTPY_STRING else f"{response}"

    def set_dynamic_values(self, endpoint, dynamic_values: dict):
        for key, value in dynamic_values.items():
            endpoint.query_params['dynamic_params'][key] = value

    def set_url_path_param(self, endpoint, replaced_path_params):
        for key, value in replaced_path_params.items():
            endpoint.url = endpoint.url.replace(key, value)

    def get_full_query_params(self, endpoint):
        return f"{endpoint.url}{QUESTION_MARK}{self.__get_iterative_dynamic_params(endpoint.query_params)}"
