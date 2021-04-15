"""
File:           product_integration.py
Author:         Dibyaranjan Sathua
Created on:     10/01/21, 10:49 pm
"""
from typing import List, Optional, Dict
from enum import IntEnum
import os
from src.woocommerce_api import WooCommerceAPI
from src.api_product_fields import ApiProductFields
from src.supplier_csv_to_woocommerce_csv import SupplierCSV2WoocommerceCSV
from src.map_csv_to_api import MapCsvToApi
from config import config


class ProductIntegration:
    """ Product Integration with WooCommerce website using API """
    class UpdateImageCode(IntEnum):
        ALlProducts = 1
        NewProducts = 2     # Update for new products or for products that don't have images

    PRODUCT_LIMIT = os.environ.get("PRODUCT_LIMIT") or 10
    UPDATE_IMAGE_MODE = UpdateImageCode.ALlProducts

    def __init__(
            self,
            csv_file: str,
            template: str,
            update_image_mode: UpdateImageCode = UpdateImageCode.ALlProducts
    ):
        self._csv_file: str = csv_file
        self._template: str = template
        self._update_image_mode: ProductIntegration.UpdateImageCode = update_image_mode
        self._api: Optional[WooCommerceAPI] = None
        self._supplier_csv_2_woocommerce_csv: Optional[SupplierCSV2WoocommerceCSV] = None
        self._map_csv_to_api: Optional[MapCsvToApi] = None
        self._api_data: Optional[List] = None
        self._woocommerce_products: Optional[List] = None
        self._api_errors: List = []
        self._products_upload_table: List[Dict] = []

    def api_setup(self):
        """ Setup WooCommerce API object """
        self._api = WooCommerceAPI(
            username=config.WooCommerceAPICred.USERNAME,
            password=config.WooCommerceAPICred.PASSWORD
        )

    def setup(self):
        """ Setup """
        print(f"Running in update image mode: {self._update_image_mode}")
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
        skus = [x[ApiProductFields.Sku] for x in self._api_data]
        # Get all the products available on WooCommerce
        self._woocommerce_products, _ = self._api.get_all_products_as_dict(skus=skus)

    def create_or_update_products(self):
        """ Create new products or update existing products """
        print(f"Using product limit of {ProductIntegration.PRODUCT_LIMIT} for batch request")
        create_product_data: List = []
        update_product_data: List = []

        for product in self._api_data:
            product_sku = product.get(ApiProductFields.Sku)
            if product_sku is None:
                print(f"Skipping processing product without {ApiProductFields.Sku}")
                continue

            # IF the products exist and the product has images, then don't update the image in
            # NewProducts mode. In all other cases update the images.
            if product_sku in self._woocommerce_products:
                print(f"Updating product for SKU {product_sku}")
                if self._update_image_mode == ProductIntegration.UpdateImageCode.NewProducts:
                    # Image already exist. So we shouldn't update the image in this mode
                    if self._woocommerce_products[product_sku].get(ApiProductFields.Images) and \
                            product.get(ApiProductFields.Images):
                        # Remove "images" key from the product
                        print(f"Removing images for SKU {product_sku}")
                        product.pop(ApiProductFields.Images)
                product_id = self._woocommerce_products[product_sku][ApiProductFields.Id]
                product.update({ApiProductFields.Id: product_id})
                update_product_data.append(product)
            else:
                print(f"Creating product for SKU {product_sku}")
                create_product_data.append(product)

        # Create a table for the status of products
        self._products_upload_table += [
            {"SKU": product.get(ApiProductFields.Sku), "Status": "Created"}
            for product in create_product_data
        ]
        self._products_upload_table += [
            {"SKU": product.get(ApiProductFields.Sku), "Status": "Updated"}
            for product in update_product_data
        ]

        # Max of 100 objects can be created or updated
        if len(create_product_data) + len(update_product_data) > ProductIntegration.PRODUCT_LIMIT:
            # Send create and update request separately
            # Send create request in a batch of 100 objects
            while create_product_data:
                response, success = self._api.create_multiple_products(
                    data=create_product_data[:ProductIntegration.PRODUCT_LIMIT]
                )
                create_product_data = create_product_data[ProductIntegration.PRODUCT_LIMIT:]

            # Send update request in a batch of 100 objects
            while update_product_data:
                response, success = self._api.update_multiple_products(
                    data=update_product_data[:ProductIntegration.PRODUCT_LIMIT]
                )
                update_product_data = update_product_data[ProductIntegration.PRODUCT_LIMIT:]
        else:
            response, success = self._api.create_or_update_products(
                create_data=create_product_data, update_data=update_product_data
            )
        self._api_errors = self._api.errors

    @property
    def api_data(self):
        return self._api_data

    @property
    def api_errors(self):
        return self._api_errors

    @property
    def product_upload_table(self):
        return self._products_upload_table


if __name__ == "__main__":
    csv_file = "/Users/dibyaranjan/Upwork/client_nick_woocommerce/brema.csv"
    template = "brema.yml"
    obj = ProductIntegration(
        csv_file=csv_file,
        template=template
    )
    obj.setup()
    obj.create_or_update_products()
