"""
Contains data model classes for 4 fact-checking pages: 
1. Politifact
2. FaktaBaari
3. FactCheck.org
4. FullFact
"""
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class PoliticFactData(BaseModel):
    statement: Optional[str] = ""
    statement_originator: Optional[str] = ""
    verdict: Optional[str] = ""
    statement_date: Optional[datetime] = None
    statement_source: Optional[str] = ""
    factchecker: Optional[str] = ""
    factcheck_date: Optional[datetime] = None
    factcheck_analysis_link: Optional[str] = ""
                    
class FaktaBaari(BaseModel):
    title: Optional[str] = ""
    category: Optional[str] = ""
    tags: List[str] = []
    url: Optional[str] = ""
    date: Optional[datetime] = None
    excerpt: Optional[str] = ""
        
class GoogleCustomSearchEngine(BaseModel):
    title: Optional[str] = ""
    source: Optional[str] = ""
    author: Optional[str] = ""
    snippet: Optional[str] = ""
    link: Optional[str] = ""
    article_published_time: Optional[datetime] = None
    article_modified_time: Optional[datetime] = None
