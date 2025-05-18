"""
Database utility functions and custom SQL expressions.
"""
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

class utcnow(expression.FunctionElement):
    """
    Custom SQL expression that returns the current UTC timestamp.
    Used as a server-side default for DateTime columns.
    """
    type = DateTime()
    inherit_cache = True