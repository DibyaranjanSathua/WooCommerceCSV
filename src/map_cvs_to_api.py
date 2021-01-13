"""
File:           map_cvs_to_api.py
Author:         Dibyaranjan Sathua
Created on:     13/01/21, 7:54 am
"""
from typing import List, Optional, Dict
import os
from src.csv_mapping import CSV_MAPPING
from src.woocommerce_api import WooCommerceAPI
from config import config


class MapCsvToApi:
    """ Class responsible for mapping CSV data to API data """
    def __init__(self, csv_data: List):
        self._csv_data: List = csv_data
        self._api_data: List = []
        self._api: Optional[WooCommerceAPI] = None
        self._categories: Dict = dict()

    def api_setup(self):
        """ Setup WooCommerce API object """
        self._api = WooCommerceAPI(
            username=config.WooCommerceAPICred.USERNAME,
            password=config.WooCommerceAPICred.PASSWORD,
        )

    def get_category_id(self, category: str):
        """ From the category name get the category id """
        # Category has hierarchy information
        cat_list = [x.strip() for x in category.split(">")]
        parents = []        # List of dict [{"id": 123}. {"id": 456}]
        for name in cat_list:
            if parents:
                woocommerce_categories = self._api.get_all_categories(
                    search=name,
                    parent=parents[-1]["id"]
                )
            else:
                woocommerce_categories = self._api.get_all_categories(search=name)
            filtered_category = self.filter_category(woocommerce_categories, name)
            parents.append({"id": filtered_category["id"]})
        return parents[-1]

    def map_csv_category(self, category: str):
        """ Map categories from csv to woocommerce api """
        list_of_categories = [x.strip() for x in category.split(",")]
        list_of_categories_id = []
        for catname in list_of_categories:
            if catname not in self._categories:
                self._categories[catname] = self.get_category_id(catname)
            list_of_categories_id.append(self._categories[catname])
        return list_of_categories_id

    def csv_category_to_api(self):
        """ Replace the CSV category with API category """
        # [{'id': 49}, {'id': 60}, {'id': 146}, {'id': 1882}]
        for data in self._api_data:
            data["categories"] = self.map_csv_category(data["categories"])
            # data["categories"] = [{'id': 49}, {'id': 60}, {'id': 146}, {'id': 1882}]

    def csv_attributes_to_api(self):
        """ Remove individual CSV attributes and create a single attributes for api """
        for data in self._api_data:
            attr1 = data.pop("attribute_1_name")
            value1 = data.pop("attribute_1_value")
            attr2 = data.pop("attribute_2_name")
            value2 = data.pop("attribute_2_value")
            attr3 = data.pop("attribute_3_name")
            value3 = data.pop("attribute_3_value")
            attr4 = data.pop("attribute_4_name")
            value4 = data.pop("attribute_4_value")
            attributes = [(attr1, value1), (attr2, value2), (attr3, value3), (attr4, value4)]
            data["attributes"] = self.map_csv_attributes(attributes)

    def csv_dimensions_to_api(self):
        """ Remove individual dimensions and create a dimensions api attribute """
        for data in self._api_data:
            length = data.pop("length")
            width = data.pop("width")
            height = data.pop("height")
            data["dimensions"] = self.map_csv_dimensions(length, width, height)

    def csv_images_to_api(self):
        """ Map csv images to api images """
        for data in self._api_data:
            data["images"] = self.map_csv_images(data["images"])

    def map(self):
        """ Map data to api """
        self.api_setup()
        for data in self._csv_data:
            mapped_data = dict()
            for key, value in data.items():
                mapped_data[CSV_MAPPING[key]] = str(value)
            self._api_data.append(mapped_data)

        self.csv_category_to_api()
        self.csv_attributes_to_api()
        self.csv_dimensions_to_api()
        self.csv_images_to_api()

    @staticmethod
    def filter_category(category_list: List, category: str):
        """ Filter out the category based on category name. It will only return one category """
        for cat in category_list:
            if cat["name"] == category:
                return cat
        return category_list.pop()

    @staticmethod
    def map_csv_dimensions(length: str, width: str, height: str):
        """ Create a dimensions attribute """
        return {
            "length": length,
            "width": width,
            "height": height
        }

    @staticmethod
    def map_csv_attributes(attributes: List[tuple]):
        """ Map all the attributes from CSV to API data """
        api_attributes = []
        for index, attrs in enumerate(attributes):
            api_attributes.append({
                "id": 0,
                "name": attrs[0],
                "position": index,
                "visible": False,
                "options": [attrs[1]]
            })
        return api_attributes

    @staticmethod
    def map_csv_images(images: str):
        """ Map csv images to api images """
        api_images = []
        images = [x.strip() for x in images.split(",")]
        for image in images:
            api_images.append({
                "src": image,
                "name": os.path.basename(image)
            })
        return api_images

    @property
    def api_data(self):
        return self._api_data


if __name__ == "__main__":
    obj = MapCsvToApi(csv_data=[])
    obj.api_setup()
    categories = "Beverage, Beverage > Ice Machines, Refrigeration, Refrigeration > Ice Machines"
    print(obj.map_csv_category(categories))
