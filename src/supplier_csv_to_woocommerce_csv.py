"""
File:           supplier_csv_to_woocommerce_csv.py
Author:         Dibyaranjan Sathua
Created on:     25/12/2020, 11:56
"""
from typing import Optional, List
import pandas as pd
import yaml
from src.template import Template


class SupplierCSV2WoocommerceCSV:
    """ This class convert Supplier CSV file to WooCommerce CSV file """

    def __init__(self, csv_file: str, template: str, output_csv: str):
        self._csv_file: str = csv_file
        self._template: str = template
        self._output_csv: str = output_csv
        self._supplier_df: Optional[pd.DataFrame] = None
        self._supplier_records: List[dict] = []
        self._woocommerce_df: Optional[pd.DataFrame] = None
        self._woocommerce_records: List[dict] = []

    def process_supplier_csv(self):
        """ Process supplier csv file and use it to render the template """
        self._supplier_df = pd.read_csv(
            self._csv_file,
            header=0,
            encoding="cp1252",
            na_filter=False
        )
        self._supplier_records = self._supplier_df.to_dict("records")

    def convert(self):
        """ Convert supplier CSV to WooCommerce CSV"""
        self.process_supplier_csv()
        for record in self._supplier_records:
            output = Template.render(template=self._template, record=record)
            output = output.replace("\r\n", "  ")
            try:
                if output:
                    self._woocommerce_records.append(yaml.full_load(output))
            except Exception as err:
                print(err)
                print(output)
        self._woocommerce_df = pd.DataFrame(self._woocommerce_records)
        self._woocommerce_df.to_csv(self._output_csv, encoding="cp1252", index=False)

    @property
    def product_records(self):
        """ Return product records """
        return self._woocommerce_records


if __name__ == "__main__":
    obj = SupplierCSV2WoocommerceCSV(
        csv_file="/Users/dibyaranjan/Upwork/client_nick_woocommerce/brema.csv",
        template="brema.yml",
        output_csv="/tmp/test456.csv"
    )
    obj.convert()
