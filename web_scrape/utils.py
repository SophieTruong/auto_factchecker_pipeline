"""
Reusable helper functions
"""

from dateutil import parser

def get_json_value(key, json_data):
    if key in json_data.keys():
        return json_data[key]
    return None

def get_meta_value(json_data, key):
    pagemap = get_json_value("pagemap", json_data)
    metatags = None if not pagemap else get_json_value("metatags", pagemap)
    meta_value = None if not metatags else get_json_value(key, metatags[0])
    if ("time" in key) and (meta_value is not None):
        meta_value = parser.parse(meta_value)
    return meta_value 
