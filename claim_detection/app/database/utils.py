"""
Database utility functions and custom SQL expressions.
"""

from typing import Optional
from sqlalchemy import cast, literal
from sqlalchemy.dialects.postgresql import REGCONFIG
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime
from sqlalchemy.sql.expression import Cast

class utcnow(expression.FunctionElement):
    """
    Custom SQL expression that returns the current UTC timestamp.
    Used as a server-side default for DateTime columns.
    """
    type = DateTime()
    inherit_cache = True

@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    '''
    A function that works like “CURRENT_TIMESTAMP” except applies the appropriate conversions so that the time is in UTC time.
    Source: https://docs.sqlalchemy.org/en/20/core/compiler.html#utc-timestamp-function
    '''
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"

def sanitize_string(text: Optional[str]) -> Optional[str]:
    """
    Sanitizes string input to prevent SQL injection and other attacks.
    
    Args:
        text: The input string to sanitize.
        
    Returns:
        The sanitized string with leading/trailing whitespace removed,
        or None if input is None.
    
    Example:
        >>> sanitize_string("  hello world  ")
        "hello world"
        >>> sanitize_string(None)
        None
    """
    if text is None:
        return None
    txt = text.strip()
    if "'" in txt:
        txt = txt.replace("'", "")
    return txt

def cast_language_literal(language: str) -> Cast:
    """
    To use TSVECTOR for PostgreSQL full text search, casts a language literal to a REGCONFIG type.
    """
    return cast(literal(language), type_=REGCONFIG)
