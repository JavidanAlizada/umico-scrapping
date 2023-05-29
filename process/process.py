from request.request import Request
from config.settings import Endpoint


class Process:
    def __init__(self, data, products, endpoint: Endpoint, request_obj: Request):
        self.__data = data
        self.__products = products
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

    def organize_products(self, products, category_map):
        category_ids = set()

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
            if category_id in category_ids:
                # Product already added to a category
                continue
            category = find_category(category_id, category_map)
            if category:
                category["Məhsullar"].append({
                    "id": product["id"],
                    "Məhsulun  adı": product["name"],
                    "Satıcı-şirkət": product["default_marketing_name"]["name"],
                    "Uğurlu sifarişlərin həcmi": str(product["default_merchant_rating"]) + "%",
                    "Skor": product["score"],
                    "Köhnə qiymət": product["old_price"],
                    "Endirimli qiymət": product["retail_price"],
                    "Xüsusiyyətlər": {}
                })
                print(f"Product:\t`` {product['name']} `` is added to category:\t`` {category['Kateqoriya']} ``")
                features = self.retrieve_product_features(product["id"])
                custom_fields = {}
                for feature in features.get("data", {}).get("custom_fields", []):
                    name = feature.get("name")
                    if name in ["Brendin ölkəsi", "İstehsalçı ölkə", "Rəng"]:
                        values = feature.get("values")
                        if len(values) == 1:
                            custom_fields[name] = values[0]
                product["custom_fields"] = custom_fields
                category_ids.add(category_id)  # Add category ID to the set
            else:
                print(f"Category ID {category_id} not found in the category map.")

    def run(self):
        print('Started process method')
        category_data = self.process()
        print('Process method executed')
        self.organize_products(self.__products, category_data["main"]["product categoryları"])
        return {"main": {"product categoryları": category_data["main"]["product categoryları"]}}
