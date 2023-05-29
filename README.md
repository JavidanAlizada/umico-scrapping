# Project Description

**Purpose**: The purpose of this program is to scrape products and categories from the Umico website and format them into a specific structure, then export them to a JSON file. The generated JSON file, `umico.json`, is located in the "result" folder. "result" folder is generated under the umico project. When folder is generating you can see it easily 

- The `category.json` file contains a list of categories scraped from the Umico website.
- The `product.json` file contains a list of products.

## Getting Started

To start the program, follow these steps:

1. Run `main.py`.
2. The `main` method in `main.py` executes the `execute` method of the `Executor` class.

## Initializing the Executor Class

To initialize the `Executor` class, you need to provide two parameters:

1. `total_page`: The number of product pages you want to scrape from Umico. Each page contains 100 products. The default value for this parameter is `MAX_PAGE_SIZE`, which is 3304.
2. `get_product_data_from_file`: If you already have scraped products and want to read the data from a file on the next run, set this parameter to `True`. Otherwise, it is `False` by default.

Example usage:

```python
executor = Executor(total_page=1, get_product_data_from_file=False)
executor.execute()