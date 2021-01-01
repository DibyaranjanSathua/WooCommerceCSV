"""
File:           woocommerce_api.py
Author:         Dibyaranjan Sathua
Created on:     27/12/2020, 23:12
"""
from typing import List
from woocommerce import API


class WooCommerceAPI:
    """ WooCommerce API """
    BASE_URL = "https://catercentral.com.au"

    def __init__(self, username: str, password: str):
        self._username: str = username
        self._password: str = password
        self._wcapi = API(
            url=WooCommerceAPI.BASE_URL,
            consumer_key=username,
            consumer_secret=password,
            version="wc/v3"
        )

    def get_all_products(self):
        """ Get a list of all products """
        endpoint = "products"
        response = self._wcapi.get(endpoint=endpoint)
        return response.json()
    
    def update_product(self, product_id: int, data: dict):
        """ Update a product based on id """
        endpoint = f"products/{product_id}"
        response = self._wcapi.put(endpoint=endpoint, data=data)
        return response.json()

    def update_multiple_products(self, data: List[dict]):
        """ Update multiple products in a single API call """
        endpoint = f"products/batch"
        data = {"update": data}
        response = self._wcapi.post(endpoint=endpoint, data=data)
        return response.json()

    def create_multiple_products(self, data: List[dict]):
        """ Create multiple products in a single API call """
        endpoint = f"products/batch"
        data = {"create": data}
        response = self._wcapi.post(endpoint=endpoint, data=data)
        return response.json()


if __name__ == "__main__":
    from slugify import slugify
    from src.supplier_csv_to_woocommerce_csv import SupplierCSV2WoocommerceCSV
    username = "ck_e34294ae2f7eaa771855d08aac0325dff6c74ace"
    password = "cs_df1a0293510c12e9d2559ef36cd2fbe4cf3ad9c4"
    obj = WooCommerceAPI(username=username, password=password)
    obj1 = SupplierCSV2WoocommerceCSV(
        csv_file="/Users/dibyaranjan/Upwork/client_nick_woocommerce/brema.csv",
        template="brema.yml"
    )
    obj1.convert()
    print(obj1.product_records)
    print(obj.get_all_products())

    # Update product
    # data = {
    #     WooCommerceAPI.ProductFields.Price: "1200",
    #     # WooCommerceAPI.ProductFields.StockQuantity: 10
    # }
    # res = obj.update_product(product_id=4386, data=data)

    # data = [
    #     {
    #         "id": 4386,
    #         "regular_price": "1201"
    #     },
    #
    #     {
    #         "id": 4441,
    #         "slug": "test-gold-product-sathualab1101",
    #         "weight": "25.75"
    #     },
    #
    #     {
    #         "id": 4442,
    #         "slug": "test-gold-product-sathualab2202",
    #         "weight": "22.5"
    #     }
    # ]
    # res = obj.update_multiple_products(data=data)

    # data = [
    #     {
    #         ApiProductFields.Name: "Test Gold Product Sathualab1101",
    #         ApiProductFields.Sku: "TESTSKU_1101",
    #         ApiProductFields.Description: "Test WooCommerce API call by SathuaLab",
    #         ApiProductFields.ShortDescription: "There is not short description",
    #         ApiProductFields.Price: "1101",
    #         ApiProductFields.StockQuantity: 1,
    #         ApiProductFields.Status: ApiProductFields.StatusOptions.Draft
    #     },
    #
    #     {
    #         ApiProductFields.Name: "Test Gold Product Sathualab2202",
    #         ApiProductFields.Sku: "TESTSKU_2202",
    #         ApiProductFields.Description: "Test WooCommerce API call by SathuaLab",
    #         ApiProductFields.ShortDescription: "There is not short description",
    #         ApiProductFields.Price: "2202",
    #         ApiProductFields.StockQuantity: 1,
    #         ApiProductFields.Status: ApiProductFields.StatusOptions.Draft,
    #         ApiProductFields.Weight: "25.75"
    #     }
    # ]
    # res = obj.create_multiple_products(data=data)

    # data = [
    #     {
    #         ApiProductFields.Name: "Test Gold Product Sathualab3303",
    #         ApiProductFields.Slug: slugify("Test Gold Product Sathualab3303"),
    #         ApiProductFields.Sku: "TESTSKU_3303",
    #         ApiProductFields.Description: "Test WooCommerce API call by SathuaLab",
    #         ApiProductFields.ShortDescription: "There is not short description",
    #         ApiProductFields.Price: "3303",
    #         ApiProductFields.StockQuantity: 1,
    #         ApiProductFields.Status: ApiProductFields.StatusOptions.Draft,
    #         ApiProductFields.Weight: "25.75",
    #         ApiProductFields.StockStatus: ApiProductFields.StockStatusOptions.InStock,
    #         ApiProductFields.SoldIndividually: True,
    #         ApiProductFields.ManageStock: True,
    #     }
    # ]
    # res = obj.create_multiple_products(data=data)
    # print(res)
