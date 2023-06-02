from config.settings import Endpoint, FilePath
from handler.file_handler import FileHandler
from process.process import Process
from request.request import Request


class Executor:
    def __fetch_categories(self, request: Request, endpoint_class, endpoint_obj):
        category_url = endpoint_obj.get_full_query_params(endpoint_class)
        request.set(category_url)
        response = request.request()
        return response.json()

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
        request_obj = Request()
        endpoint = Endpoint()
        file_handler = FileHandler()
        self.__clear_file(FilePath.UMICO_CATEGORY_AND_PRODUCT_JSON_FILE_FULL_PATH, file_handler)
        categories = self.__fetch_categories(request_obj, Endpoint.Category, endpoint)
        print(f'Categories fetched ...')
        self.__write_to_file(categories, FilePath.UMICO_CATEGORY_JSON_FILE_FULL_PATH, file_handler)
        process_obj = Process(categories['data'], endpoint, request_obj)
        print('Process running now...')
        json_result_of_process = process_obj.run()

        self.__write_to_file(json_result_of_process, FilePath.UMICO_CATEGORY_AND_PRODUCT_JSON_FILE_FULL_PATH,
                             file_handler)
