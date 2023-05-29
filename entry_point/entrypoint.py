from config.settings import Endpoint, FilePath
from handler.file_handler import FileHandler
from process.process import Process
from request.request import Request


class Executor:

    def __init__(self, total_page: int = 3304, get_product_data_from_file: bool = False):
        self.__product_max_total_page = 3304
        if total_page > self.__product_max_total_page:
            self.__total_page = self.__product_max_total_page
        else:
            self.__total_page = total_page

        self.__page_start_from = 1
        self.__get_product_data_from_file = get_product_data_from_file

    def __fetch_categories(self, request: Request, endpoint_class, endpoint_obj):
        category_url = endpoint_obj.get_full_query_params(endpoint_class)
        request.set(category_url)
        response = request.request()
        return response.json()

    def __fetch_products(self, request: Request, endpoint_class, endpoint_obj):
        products = []
        page = self.__page_start_from
        # total_pages = 3304
        total_pages = self.__total_page
        product_url = endpoint_obj.get_full_query_params(endpoint_class)
        request.set(product_url)
        while page <= total_pages:
            print(f"Retrieving product for {page} page")
            endpoint_obj.set_dynamic_values(endpoint_class, {'page': page})
            response = request.request()
            if response.status_code == 200:
                product_list = response.json()
                products.extend(product_list["products"])
                page += 1
            else:
                print(f"Failed to retrieve products for page {page}.")
                break
        return products

    def __write_to_file(self, data, file, handler: FileHandler):
        handler.set_data(data).set_json_file(file)
        handler.write_to_json_file()

    def __get_from_file(self, file, handler: FileHandler):
        handler.set_json_file(file)
        return handler.read_from_file()

    def __clear_file(self, file, handler: FileHandler):
        handler.set_json_file(file)
        handler.clear_file()

    def execute(self):
        should_fetch_product_data_from_file = self.__get_product_data_from_file
        request_obj = Request()
        endpoint = Endpoint()
        file_handler = FileHandler()
        self.__clear_file(FilePath.UMICO_CATEGORY_AND_PRODUCT_JSON_FILE_FULL_PATH, file_handler)
        categories = self.__fetch_categories(request_obj, Endpoint.Category, endpoint)
        self.__write_to_file(categories, FilePath.UMICO_CATEGORY_JSON_FILE_FULL_PATH, file_handler)
        print(f'Categories fetched ...')

        if should_fetch_product_data_from_file:
            # TODO: Use for dev env or if product.json contains some parts of products data
            products = self.__get_from_file(FilePath.UMICO_PRODUCT_JSON_FILE_FULL_PATH, file_handler)
        else:
            # TODO:  Use only for production-ready or if product.json is empty
            products = self.__fetch_products(request_obj, Endpoint.Product, endpoint)
            self.__write_to_file(products, FilePath.UMICO_PRODUCT_JSON_FILE_FULL_PATH, file_handler)

        process_obj = Process(categories['data'], products, endpoint, request_obj)
        print('Process running now...')
        json_result_of_process = process_obj.run()

        self.__write_to_file(json_result_of_process, FilePath.UMICO_CATEGORY_AND_PRODUCT_JSON_FILE_FULL_PATH,
                             file_handler)
