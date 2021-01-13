"""
File:           custom_filters.py
Author:         Dibyaranjan Sathua
Created on:     29/12/2020, 15:17
"""
from typing import Union
import re
import os


def remove_leading_asterisk(string: str):
    """ Removing leading asterisk characters """
    regex = re.compile(r"\s*\*\s*")
    return regex.sub("", string)


def blank_if_zero(value: Union[float, int]):
    """ Remove zero from the entry. If the value is zero, make it blank """
    if value == 0:
        return ""
    return value


def file_exist(filename: str, base_path: str):
    """ Check if file exist on the server """
    if not filename:
        return False
    filepath = os.path.join("~", base_path, filename)
    if os.path.isfile(filepath):
        return True
    return False
