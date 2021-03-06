"""
File:           custom_filters.py
Author:         Dibyaranjan Sathua
Created on:     29/12/2020, 15:17
"""
from typing import Union
import re
import os
import ftfy
import requests


def remove_leading_asterisk(string: str):
    """ Removing leading asterisk characters. Used in brema """
    regex = re.compile(r"\s*\*\s*")
    return regex.sub("", string)


def blank_if_zero(value: Union[float, int]):
    """ Remove zero from the entry. If the value is zero, make it blank. Used in brema """
    if value == 0:
        return ""
    return value


def blank_if_nan0(value: str):
    """ Return blank if not a number or zero. """
    try:
        num = int(value)
        return "" if num == 0 else num
    except: return ""


def remove_nan_suffix(value: str):
    """ Remove suffix that's not a number """
    regex = re.compile(r"[^\d]+$")
    return regex.sub("", value, re.IGNORECASE + re.MULTILINE)


def file_exist(filename: str, base_path: str):
    """ Check if file exist on the server. Used in brema """
    if not filename:
        return False
    filepath = os.path.join(base_path, filename)
    if os.path.isfile(filepath):
        return True
    return False


def remove_trailing_bromic(string: str):
    """ Remove bromic from the end of the string. Used in bromic """
    regex = re.compile(r"\s+[^\s]\s+Bromic(?:\s+Refrigeration)?\s*$")
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
        local_filepath = os.path.join(base_path, path.lstrip("/"))
        if os.path.isfile(local_filepath):
            output += f'<a href="{path_prefix}{path}" target="_blank">{name}</a> | '

    output = output.strip().strip("|").strip()
    return output


def create_image(string: str, path_prefix: str, split_char: str = ","):
    """ Image path. Used in bromic """
    images = [f"{path_prefix}{x.strip()}" for x in string.split(split_char)]
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


def filter_price(value: str):
    """ Remove non-numericals from price. Return blank if no valid price remains """
    regex = re.compile(r"[^\d.]")
    try: return float(regex.sub("", value))
    except: return ""


def filter_poa_price(value: Union[str, int]):
    """ Check if price is POA return blank string. Used in bromic """
    return value if type(value) == int else "" if "POA" in value.upper() else value


def filter_na_price(string: str):
    """ Check if price is N/A return blank string. Used in kci """
    return "" if "N/A" in string.upper() else string


def volume_is_in_liter(string: str):
    """ Check if the volumn is in Litre unit. Used in bromic """
    return string.lower().endswith("l")


def volume_is_in_kg(string: str):
    """ check if volume is in kg. Used in bromic """
    return string.lower().endswith("kg")


def swap_sku_name_order(name: str, sku: str):
    """ If SKU is at beginning of name, place at the end. Used in FED """
    return name.replace(sku, "").strip(" -") + " - " + sku if name.startswith(sku) else name


def replace_newline_with_space(name: str):
    """ Replace newline character with space. Used in KCI  """
    return name.replace("\n", " ")


def split_string(string: str, char: str):
    """ Split string and return a list """
    return [x.strip() for x in string.split(char)]


def brochure_files(string: str, path_prefix: str, base_path: str):
    """ Create brochure links in description. Used in KCI """
    # Brohure has \n\n which will create an empty string
    files = [x for x in string.split("\n") if x]
    output = ""
    if len(files) == 1:
        file = files.pop()
        # base path is used to check if file exists or not
        # path will have leading /. We have to remove it while using in os.path.join
        local_filepath = os.path.join(base_path, file)
        if os.path.isfile(local_filepath):
            output = f'<a href="{path_prefix}{file}" target="_blank">Brochure</a>'
    else:
        counter = 1
        for file in files:
            local_filepath = os.path.join(base_path, file)
            if os.path.isfile(local_filepath):
                output += f'<a href="{path_prefix}{file}" target="_blank">Brochure {counter}</a> | '
                counter += 1
        output = output.strip().strip("|").strip()
    return output


def check_remote_image_exists(string: str, path_prefix: str, split_char: str = ","):
    """ Split the images and check if they exist. Return a list of images which exists """
    images = [f"{path_prefix}{x.strip()}" for x in string.split(split_char)]
    images_exist = []
    for image in images:
        response = requests.head(image)
        if response.ok:
            images_exist.append(image)
    return ",".join(images_exist)


def regex_replace(string: str, search: str, replace: str = "", flags: int = 0):
    """ Multi-purpose regex replace filter """
    regex = re.compile(search)
    return regex.sub(replace, string, flags)


def esc_quot(string: str):
    """ HTML escape quotes """
    return string.replace('"', "&quot;")


def esc_special_symbol(string: str):
    """ Replace special symbol with html """
    ampersand_regex = re.compile("&(?!amp;)")
    return ampersand_regex.sub("&amp;", string)


def get_existing_images(string: str, base_path: str, path_prefix: str, split_char: str = ","):
    """
    Return list of images that exist. Used im KCI.
    This is combination of file_exist and create_image functions
    """
    images = []
    input_images = [x.strip() for x in string.split(split_char)]
    for image in input_images:
        filepath = os.path.join(base_path, image)
        if os.path.isfile(filepath):
            images.append(f"{path_prefix}{image}")
    return images


def remove_empty_lines(string: str):
    """ Remove empty lines. Used in Rational  """
    return "\n".join([x for x in string.split("\n") if x])
