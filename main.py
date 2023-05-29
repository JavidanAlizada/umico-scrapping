from entry_point.entrypoint import Executor

if __name__ == '__main__':
    # MAX_TOTAL_PRODUCT_PAGE = 3304
    executor = Executor(total_page=1, get_product_data_from_file=False)
    executor.execute()
