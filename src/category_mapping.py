"""
File:           category_mapping.py
Author:         Dibyaranjan Sathua
Created on:     15/04/21, 11:48 pm
"""
from typing import Tuple
import pandas as pd


class CategoryMapper:
    """ Category Mapper """

    def __init__(self, main_csv_file: str, mapping_file: str):
        self.main_csv_file = main_csv_file
        self.mapping_file = mapping_file
        self.main_df = None

    def map(self, column_name: str, mapping_file_column: Tuple):
        """
        Run mapper.
        column_name: Name of the column in the main csv file that needs to be mapped
        mapping_file_column: Column name in mapping file.
        """
        category_mapping_dict = dict()
        mapping_df = pd.read_csv(
            self.mapping_file,
            header=0,
            na_filter=False
        )
        # from the df, create a mapping dictionary
        for i in range(len(mapping_df)):
            category_mapping_dict[mapping_df.loc[i, mapping_file_column[0]]] = \
                mapping_df.loc[i, mapping_file_column[1]]
        self.main_df = pd.read_csv(
            self.main_csv_file,
            header=0,
            na_filter=False
        )
        self.main_df[column_name] = self.main_df[column_name].apply(
            lambda x: ", ".join(
                [
                    category_mapping_dict.get(cat.strip())
                    for cat in x.split(",") if category_mapping_dict.get(cat.strip())
                ]
            )
        )

    def save_to_csv(self, output_csv):
        """ Save the modified dataframe to csv """
        self.main_df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    main_csv_file = "/Users/dibyaranjan/Upwork/client_nick_woocommerce/Fedau_csvfeed_20210219.csv"
    mapping_file = "/Users/dibyaranjan/Upwork/client_nick_woocommerce/Completed-FED-CatMap.csv"
    column = "Categories"
    mapping_file_column = ("FED Category", "Our Category")
    mapper = CategoryMapper(main_csv_file=main_csv_file, mapping_file=mapping_file)
    mapper.map(column_name=column, mapping_file_column=mapping_file_column)
    mapper.save_to_csv("/tmp/test_category_map.csv")
