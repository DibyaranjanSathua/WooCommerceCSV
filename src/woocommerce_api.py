"""
File:           woocommerce_api.py
Author:         Dibyaranjan Sathua
Created on:     27/12/2020, 23:12
"""
from typing import List, Dict, Optional, Tuple
import os
from woocommerce import API
from src.api_product_fields import ApiProductFields


class WooCommerceAPI:
    """ WooCommerce API """
    BASE_URL = "https://catercentral.com.au"

    def __init__(self, username: str, password: str):
        self._username: str = username
        self._password: str = password
        timeout = os.environ.get("API_TIMEOUT") or 600
        self._wcapi = API(
            url=WooCommerceAPI.BASE_URL,
            consumer_key=username,
            consumer_secret=password,
            version="wc/v3",
            timeout=timeout
        )
        print(f"API timeout set to {timeout}")

    def get_all_products(self, skus: Optional[List] = None):
        """ Get a list of all products """
        success = True
        endpoint = "products"
        params = {"per_page": 100}
        if skus is None:
            response = self._wcapi.get(endpoint=endpoint, params=params)
            return response.json()

        products = []
        while skus:
            skus_in_request = skus[:100]
            skus = skus[100:]
            params["sku"] = ",".join(skus_in_request)
            params["per_page"] = len(skus_in_request)
            response = self._wcapi.get(endpoint=endpoint, params=params)
            if response.ok:
                products += response.json()
            else:
                success = False
        return products, success

    def get_all_products_as_dict(self, skus: Optional[List] = None) -> Tuple[Dict, bool]:
        """ Convert list of products to dict of products with key as SKU """
        products, success = self.get_all_products(skus)
        return {product[ApiProductFields.Sku]: product for product in products}, success
    
    def update_product(self, product_id: int, data: dict):
        """ Update a product based on id """
        success = False
        endpoint = f"products/{product_id}"
        response = self._wcapi.put(endpoint=endpoint, data=data)
        if response.status_code == 200:
            success = True
        return response.json(), success

    def update_multiple_products(self, data: List[dict]):
        """ Update multiple products in a single API call """
        success = False
        endpoint = f"products/batch"
        data = {"update": data}
        response = self._wcapi.post(endpoint=endpoint, data=data)
        if response.status_code == 200:
            success = True
        return response.json(), success

    def create_multiple_products(self, data: List[dict]):
        """ Create multiple products in a single API call """
        success = False
        endpoint = f"products/batch"
        data = {"create": data}
        response = self._wcapi.post(endpoint=endpoint, data=data)
        if response.status_code in (200, 201):
            success = True
        return response.json(), success

    def create_or_update_products(self, create_data: List[Dict], update_data: List[Dict]):
        """ Create or Update products in batch in a single API call """
        # Max of 100 objects can be created or updated
        success = False
        endpoint = f"products/batch"
        data = {
            "create": create_data,
            "update": update_data
        }
        response = self._wcapi.post(endpoint=endpoint, data=data)
        if response.status_code == 200:
            print("create or update product request is success")
            success = True
        return response.json(), success

    def get_all_categories(
            self,
            search: Optional[str] = None,
            per_page: Optional[int] = None,
            parent: Optional[int] = None
    ):
        """ Get list of categories """
        success = False
        endpoint = f"products/categories"
        params = {}
        if search is not None:
            params["search"] = search
        if per_page is not None:
            params["per_page"] = per_page
        if parent is not None:
            params["parent"] = parent
        response = self._wcapi.get(endpoint=endpoint, params=params)
        if response.status_code == 200:
            success = True
        return response.json(), success

    def get_all_attributes(self):
        """ Get a list of product attributes """
        success = False
        endpoint = f"products/attributes"
        response = self._wcapi.get(endpoint=endpoint)
        if response.status_code == 200:
            success = True
        return response.json(), success


if __name__ == "__main__":
    from config import config
    from src.supplier_csv_to_woocommerce_csv import SupplierCSV2WoocommerceCSV
    obj = WooCommerceAPI(
        username=config.WooCommerceAPICred.USERNAME,
        password=config.WooCommerceAPICred.PASSWORD
    )
    # obj1 = SupplierCSV2WoocommerceCSV(
    #     csv_file="/Users/dibyaranjan/Upwork/client_nick_woocommerce/brema.csv",
    #     template="brema.yml"
    # )
    # obj1.convert()
    # print(obj1.product_records)
    # print(obj.get_all_products())
    # result = obj.get_all_categories(search="Beverage")
    result = obj.get_all_attributes()
    print(result)
