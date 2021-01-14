"""
File:           product_integration.py
Author:         Dibyaranjan Sathua
Created on:     10/01/21, 10:49 pm
"""
from typing import List, Optional, Dict
from src.woocommerce_api import WooCommerceAPI
from src.api_product_fields import ApiProductFields
from src.supplier_csv_to_woocommerce_csv import SupplierCSV2WoocommerceCSV
from src.map_cvs_to_api import MapCsvToApi
from config import config


class ProductIntegration:
    """ Product Integration with WooCommerce website using API """
    PRODUCT_LIMIT = 20

    def __init__(self, csv_file: str, template: str):
        self._csv_file: str = csv_file
        self._template: str = template
        self._api: Optional[WooCommerceAPI] = None
        self._supplier_csv_2_woocommerce_csv: Optional[SupplierCSV2WoocommerceCSV] = None
        self._map_csv_to_api: Optional[MapCsvToApi] = None
        self._api_data: Optional[List] = None

    def api_setup(self):
        """ Setup WooCommerce API object """
        self._api = WooCommerceAPI(
            username=config.WooCommerceAPICred.USERNAME,
            password=config.WooCommerceAPICred.PASSWORD
        )

    def setup(self):
        """ Setup """
        self.api_setup()
        self._supplier_csv_2_woocommerce_csv = SupplierCSV2WoocommerceCSV(
            csv_file=self._csv_file,
            template=self._template
        )
        self._supplier_csv_2_woocommerce_csv.convert()
        self._map_csv_to_api = MapCsvToApi(
            csv_data=self._supplier_csv_2_woocommerce_csv.product_records
        )
        self._map_csv_to_api.map()
        self._api_data = self._map_csv_to_api.api_data

    def create_or_update_products(self):
        """ Create new products or update existing products """
        create_product_data: List = []
        update_product_data: List = []
        # Get all the products available on WooCommerce
        woocommerce_products: Dict = self._api.get_all_products_as_dict()

        for product in self._api_data:
            product_sku = product.get(ApiProductFields.Sku)
            if product_sku is None:
                print(f"Skipping processing product without {ApiProductFields.Sku}")
                continue

            if product_sku in woocommerce_products:
                print(f"Updating product for SKU {product_sku}")
                product_id = woocommerce_products[product_sku][ApiProductFields.Id]
                product.update({ApiProductFields.Id: product_id})
                update_product_data.append(product)
            else:
                print(f"Creating product for SKU {product_sku}")
                create_product_data.append(product)

        # Max of 100 objects can be created or updated
        if len(create_product_data) + len(update_product_data) > ProductIntegration.PRODUCT_LIMIT:
            # Send create and update request separately
            # Send create request in a batch of 100 objects
            while create_product_data:
                self._api.create_multiple_products(
                    data=create_product_data[:ProductIntegration.PRODUCT_LIMIT]
                )
                create_product_data = create_product_data[ProductIntegration.PRODUCT_LIMIT:]

            # Send update request in a batch of 100 objects
            while update_product_data:
                self._api.update_multiple_products(
                    data=update_product_data[:ProductIntegration.PRODUCT_LIMIT]
                )
                update_product_data = update_product_data[ProductIntegration.PRODUCT_LIMIT:]
        else:
            self._api.create_or_update_products(
                create_data=create_product_data, update_data=update_product_data
            )

    @property
    def api_data(self):
        return self._api_data

    @property
    def api_success(self):
        return self._api.success


if __name__ == "__main__":
    csv_file = "/Users/dibyaranjan/Upwork/client_nick_woocommerce/brema.csv"
    template = "brema.yml"
    obj = ProductIntegration(
        csv_file=csv_file,
        template=template
    )
    obj.setup()
    obj.create_or_update_products()
