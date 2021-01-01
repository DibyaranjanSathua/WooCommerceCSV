"""
File:           custom_filters.py
Author:         Dibyaranjan Sathua
Created on:     29/12/2020, 15:17
"""
import re


def remove_leading_asterisk(string: str):
    """ Removing leading asterisk characters """
    regex = re.compile(r"\s*\*\s*")
    return regex.sub("", string)
