"""
File:           check_categories.py
Author:         Dibyaranjan Sathua
Created on:     11/03/21, 2:23 pm
"""
from typing import List, Dict, Optional
from src.woocommerce_api import WooCommerceAPI
from config import config


class CheckCategories:
    """ Class responsible for checking if the categories exist on WooCommerce """

    def __init__(self, woocommerce_records: List[Dict]):
        self._woocommerce_records = woocommerce_records
        self._api: Optional[WooCommerceAPI] = None
        self._categories: Dict = dict()
        self._missing_categories: List = []

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
                woocommerce_categories, _ = self._api.get_all_categories(
                    search=name,
                    parent=parents[-1]["id"]
                )
            else:
                woocommerce_categories, _ = self._api.get_all_categories(search=name)

            if not woocommerce_categories:
                print(f"No woocommerce categories found for name {name}")
                self._missing_categories.append(name)
                return parents[-1]
            filtered_category = self.filter_category(woocommerce_categories, name)
            parents.append({"id": filtered_category["id"]})
        return parents[-1]

    def find_missing_category(self):
        """ Find missing categories  """
        self.api_setup()
        for record in self._woocommerce_records:
            category = record["Categories"]
            list_of_categories = [x.strip() for x in category.split(",")]
            for catname in list_of_categories:
                if catname not in self._categories:
                    self._categories[catname] = self.get_category_id(catname)

    @staticmethod
    def filter_category(category_list: List, category: str):
        """ Filter out the category based on category name. It will only return one category """
        for cat in category_list:
            if cat["name"] == category:
                return cat
        return category_list.pop()

    @property
    def missing_categories(self):
        return self._missing_categories
