from request.request import Request
from config.settings import Endpoint
import requests.exceptions


class Process:
    def __init__(self, data, endpoint: Endpoint, request_obj: Request):
        self.__data = data
        self.__endpoint = endpoint
        self.__request_obj = request_obj

    def process(self):
        result = {"main": {"product categoryları": []}}
        category_map = {}

        def build_category(category):
            category_data = {
                "category_id": category["id"],
                "Kateqoriya": category["name"],
                "Sub Kateqoriya": [],
                "Məhsullar": []
            }
            if category["id"] in category_map:
                category_data["Sub Kateqoriya"] = category_map[category["id"]]["Sub Kateqoriya"]
                category_data["Məhsullar"] = category_map[category["id"]]["Məhsullar"]
            return category_data

        def traverse(category):
            current_category = build_category(category)
            if category["parent_id"]:
                parent_category = category_map.get(category["parent_id"])
                if not parent_category:
                    # Parent category not found by parent_id, look for ref_category_id
                    for parent_category in category_map.values():
                        if parent_category.get("category_id") == category["ref_category_id"]:
                            break
                    else:
                        # Parent category not found by ref_category_id either
                        parent_category = None

                if parent_category:
                    parent_category["Sub Kateqoriya"].append(current_category)
                else:
                    result["main"]["product categoryları"].append(current_category)
            else:
                result["main"]["product categoryları"].append(current_category)

            category_map[category["id"]] = current_category

            for child_id in category["child_ids"]:
                child_category = next((c for c in self.__data if c["id"] == child_id), None)
                if child_category:
                    traverse(child_category)

        for category in self.__data:
            if not category["parent_id"]:
                traverse(category)

        return result

    def retrieve_product_features(self, product_id):
        try:
            endpoint = Endpoint.ProductFeatures
            replaced_path_param = {'{product_id}': str(product_id)}
            self.__endpoint.set_url_path_param(endpoint, replaced_path_param)
            url = self.__endpoint.get_full_query_params(endpoint)
            self.__request_obj.set(url)
            response = self.__request_obj.request()
            if response.status_code == 200:
                features = response.json()
                return features
            else:
                print(f"Failed to retrieve features for product ID {product_id}.")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while retrieving product features for ID {product_id}: {e}")
            return None

    def retrieve_products_by_category(self, category_id):
        endpoint = Endpoint.ProductByCategory

        is_not_locale_az = True
        current_page = 1
        products = []
        per_page = 100
        while is_not_locale_az:
            replaced_path_param = {
                'q%5Bcategory_id_in%5D': str(category_id),
                'page': str(current_page),
                'per_page': str(per_page)
            }
            self.__endpoint.set_dynamic_values(endpoint, replaced_path_param)
            url = self.__endpoint.get_full_query_params(endpoint)
            self.__request_obj.set(url)
            response = self.__request_obj.request()
            not_last_extended = True
            if response.status_code == 200:
                if response.json().get("locale") == 'az':
                    response_json = response.json()
                    response_product = response_json.get("products", [])
                    meta = response_json.get('meta')
                    if meta['total_entries'] > per_page:
                        products.extend(response_product)
                        total_pages = meta['total_pages']
                        current_page += 1
                        not_last_extended = False
                        while current_page < total_pages:
                            replaced_path_param['page'] = str(current_page)
                            self.__endpoint.set_dynamic_values(endpoint, replaced_path_param)
                            url = self.__endpoint.get_full_query_params(endpoint)
                            self.__request_obj.set(url)
                            response = self.__request_obj.request()
                            if response.status_code == 200:
                                if response.json().get("locale") == 'az':
                                    response_json = response.json()
                                    response_product = response_json.get("products", [])
                                    products.extend(response_product)
                                    current_page += 1
                    is_not_locale_az = False
                    if not_last_extended:
                        products.extend(response_product)

            else:
                print(f"Failed to retrieve products for category ID {category_id}.")
                return []

        return products

    def organize_products(self, products, category_map):
        category_ids = set()
        product_ids = set()

        def find_category(category_idd, categories):
            for category in categories:
                if category["category_id"] == category_idd:
                    return category
                sub_categories = category.get("Sub Kateqoriya", [])
                result = find_category(category_idd, sub_categories)
                if result:
                    return result
            return None

        for product in products:
            category_id = product["category_id"]
            # if category_id in category_ids:
                # Product already added to a category
                # continue
            # category = find_category(category_id, category_map)
            category = category_map[0]
            if category and product['id'] not in product_ids:
                category["Məhsullar"].append({
                    "id": product["id"],
                    "Məhsulun adı": product["name"],
                    "Satıcı-şirkət":  product["default_marketing_name"]["name"] if product["default_marketing_name"] else None,
                    "Uğurlu sifarişlərin həcmi": str(product["default_merchant_rating"]) + "%" if product["default_merchant_rating"] else None,
                    "Skor": product["score"],
                    "Köhnə qiymət": product["old_price"],
                    "Endirimli qiymət": product["retail_price"],
                    "Xüsusiyyətlər": {}
                })
                print(f"Product:\t``{product['id']} -- {product['name']} `` is added to category:\t`` {category_id} -- {category['Kateqoriya']} ``")
                features = self.retrieve_product_features(product["id"])
                custom_fields = {}
                if features:
                    for feature in features.get("data", {}).get("custom_fields", []):
                        name = feature.get("name")
                        if name in ["Brendin ölkəsi", "İstehsalçı ölkə", "Rəng"]:
                            values = feature.get("values")
                            if len(values) == 1:
                                custom_fields[name] = values[0]
                    product["custom_fields"] = custom_fields
                    category_ids.add(category_id)  # Add category ID to the set
                    product_ids.add(product["id"])
            else:
                print(f"Category ID {category_id} not found in the category map.")

        for category in category_map:
            category["Məhsullar"] = [product for product in category["Məhsullar"] if product["id"] in product_ids]


    def run(self):
        print('Started process method')
        category_data = self.process()
        print('Process method executed')

        subcategory_ids = set()

        def gather_subcategory_ids(category):
            if not category["Sub Kateqoriya"]:
                subcategory_ids.add(category["category_id"])
            else:
                for subcategory in category["Sub Kateqoriya"]:
                    gather_subcategory_ids(subcategory)

        for category in category_data["main"]["product categoryları"]:
            gather_subcategory_ids(category)

        print("Subcategory IDs:", subcategory_ids)

        def process_categories(categories):
            for category in categories:
                category_id = category["category_id"]
                if category_id in subcategory_ids:
                    products = self.retrieve_products_by_category(category_id)
                    self.organize_products(products, [category])
                if category["Sub Kateqoriya"]:
                    process_categories(category["Sub Kateqoriya"])

        process_categories(category_data["main"]["product categoryları"])

        return {"main": {"product categoryları": category_data["main"]["product categoryları"]}}