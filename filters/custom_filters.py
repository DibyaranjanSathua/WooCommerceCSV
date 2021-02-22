"""
File:           custom_filters.py
Author:         Dibyaranjan Sathua
Created on:     29/12/2020, 15:17
"""
from typing import Union
import re
import os
import ftfy


def remove_leading_asterisk(string: str):
    """ Removing leading asterisk characters. Used in brema """
    regex = re.compile(r"\s*\*\s*")
    return regex.sub("", string)


def blank_if_zero(value: Union[float, int]):
    """ Remove zero from the entry. If the value is zero, make it blank. Used in brema """
    if value == 0:
        return ""
    return value


def file_exist(filename: str, base_path: str):
    """ Check if file exist on the server. Used in brema """
    if not filename:
        return False
    filepath = os.path.join(os.path.expanduser("~"), base_path, filename)
    if os.path.isfile(filepath):
        return True
    return False


def remove_trailing_bromic(string: str):
    """ Remove bromic from the end of the string. Used in bromic """
    regex = re.compile(r"\s*-\s*Bromic\s*$")
    return regex.sub("", string, re.IGNORECASE)


def add_leading_bromic(string: str):
    """ Add leading bromic if not present. Used in bromic """
    regex = re.compile(r"^\s*Bromic")
    if regex.search(string) is None:
        string = f"Bromic {string}"
    regex = re.compile(r"^\s*Bromic\s*-\s*")
    # Remove the dash after Bromic
    return regex.sub("Bromic ", string, re.IGNORECASE)


def remove_div_span_tags(string: str):
    """ Remove div and span tags. Used in bromic """
    div_start_regex = re.compile(r"<div.*?>")
    div_end_regex = re.compile(r"</div>")
    span_start_regex = re.compile(r"<span.*?>")
    span_end_regex = re.compile(r"</span>")
    output_string = div_start_regex.sub("", string)
    output_string = div_end_regex.sub("", output_string)
    output_string = span_start_regex.sub("", output_string)
    output_string = span_end_regex.sub("", output_string)
    return output_string


def non_zero_warranty(string: str):
    """ Return 1 if the warrant value if zero """
    return "1" if string == "0" else string


def product_files(string: str, path_prefix: str, base_path: str):
    """ Extract product files from additional attributes. Used in bromic """
    regex = re.compile(r"products_file_text=(.*?),")
    match_str = regex.search(string)
    if match_str is None:
        return ""
    product_file_text = match_str.group(1)
    files = product_file_text.split("|")
    output = ""
    for file in files:
        if not file:
            continue
        name, path = file.split("&")
        # Remove Download from the name
        name = name.replace("Download", "").strip()
        # base path is used to check if file exists or not
        # path will have leading /. We have to remove it while using in os.path.join
        local_filepath = os.path.join(os.path.expanduser("~"), base_path, path.lstrip("/"))
        if os.path.isfile(local_filepath):
            output += f'<a href="{path_prefix}{path}" target="_blank">{name}</a> | '

    output = output.strip().strip("|").strip()
    return output


def create_image(string: str, path_prefix: str):
    """ Image path. Used in bromic """
    images = [f"{path_prefix}{x.strip()}" for x in string.split(",")]
    return ",".join(images)


def format_description(string: str):
    """ Format description. Used in bromic """
    def remove_leading_line_space(match_str):
        return ""
    regex = re.compile(r"^\s+", re.MULTILINE)
    return regex.sub(remove_leading_line_space, string)


def repair_utf8_encoding(string: str):
    """ Repair utf-8 encoding containing iso-8599 """
    return ftfy.fix_encoding(string)


def format_volume(string: str):
    """ Format volume. Used in bromic """
    regex = re.compile(r"(\d+)")
    match_str = regex.search(string)
    if match_str is None:
        return 0
    return float(match_str.group(1))


def filter_poa_price(string: str):
    """ Check if price is POA return blank string. Used in bromic """
    return "" if "POA" in string.upper() else string


def volume_is_in_liter(string: str):
    """ Check if the volumn is in Litre unit. Used in bromic """
    return string.lower().endswith("l")


def volume_is_in_kg(string: str):
    """ check if volume is in kg. Used in bromic """
    return string.lower().endswith("kg")
