# Project Description

**Purpose**: The purpose of this program is to scrape products and categories from the Umico website and format them into a specific structure, then export them to a JSON file. The generated JSON file, `umico.json`, is located in the "result" folder. "result" folder is generated under the umico project. When folder is generating you can see it easily 

- The `category.json` file contains a list of categories scraped from the Umico website.
- The `product.json` file contains a list of products.

## Getting Started

To start the program, follow these steps:

1. Run `main.py`.
2. The `main` method in `main.py` executes the `execute` method of the `Executor` class.

## Initializing the Executor Class

Example usage:

```python
executor = Executor()
executor.execute()