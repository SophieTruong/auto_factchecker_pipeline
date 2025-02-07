"""
Source: https://manishankarjaiswal.medium.com/simplifying-url-creation-in-python-with-the-builder-design-pattern-16495a82cb79
"""
from urllib.parse import urlencode

class URLBuilder:
    def __init__(self):
        self.scheme = "http"
        self.authority = ""
        self.port = None
        self.path = ""
        self.params = {}

    def set_scheme(self, scheme):
        self.scheme = scheme
        return self

    def set_authority(self, authority):
        self.authority = authority
        return self

    def set_port(self, port):
        self.port = port
        return self

    def set_path(self, path):
        self.path = path
        return self

    def add_param(self, key, value):
        self.params[key] = value
        return self

    def build(self):
        url = f"{self.scheme}://{self.authority}"
        if self.port:
            url += f":{self.port}"
        if self.path:
            url += f"/{self.path}"
        if self.params:
            query_string = urlencode(self.params)
            url += f"?{query_string}"
        return url
