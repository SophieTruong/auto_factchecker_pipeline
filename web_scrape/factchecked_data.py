"""
Contains data model classes for 4 fact-checking pages: 
1. Politifact
2. FaktaBaari
3. FactCheck.org
4. FullFact
"""
from datetime import datetime
from typing_extensions import TypedDict

class PoliticFactData(TypedDict, total=False):
    def __init__(self):
        self.statement : str = ""
        self.statement_originator : str = ""
        self.verdict : str = ""
        self.statement_date : datetime | None = None
        self.statement_source : str = ""
        self.factchecker : str = ""
        self.factcheck_date : datetime | None = None
        self.factcheck_analysis_link : str = ""
                    
class FaktaBaari(TypedDict, total=False):
    def __init__(self):
        self.title : str = ""
        self.category : str = ""
        self.tags : list[str] = []
        self.url : str = ""
        self.date : datetime | None = None
        self.excerpt : str = ""
        
class GoogleCustomSearchEngine(TypedDict, total=False):
    def __init__(self):
        self.title : str = ""
        self.source : str = ""
        self.author : str = ""
        self.snippet : str = ""
        self.link : str = ""
        self.article_published_time : datetime | None = None
        self.article_modified_time : datetime | None = None

class FactCheckOrg(GoogleCustomSearchEngine):
    pass

class FullFact(GoogleCustomSearchEngine):
    pass

