"""
File:           template.py
Author:         Dibyaranjan Sathua
Created on:     25/12/2020, 21:07
"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from filters import custom_filters


class Template:
    """ Render a template using jinja2 engine """
    template_loader = Environment(
        loader=FileSystemLoader(searchpath=Path(__file__).parents[1] / "templates"),
        trim_blocks=True,
        lstrip_blocks=True
    )

    @classmethod
    def render(cls, template, record):
        """ Render a template and return the string output """
        custom_filters_dict = cls.get_all_custom_filters()
        for filter_name, filter_obj in custom_filters_dict.items():
            cls.template_loader.filters[filter_name] = filter_obj
        template = cls.template_loader.get_template(template)
        output = template.render(record=record)
        return output

    @staticmethod
    def get_all_custom_filters():
        """ Get list of all custom filters """
        return {
            x: getattr(custom_filters, x)
            for x in dir(custom_filters) if callable(getattr(custom_filters, x))
        }
