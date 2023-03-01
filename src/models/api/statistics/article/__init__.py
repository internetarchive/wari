from typing import Optional

from pydantic import BaseModel, Extra

from src.models.api.statistics.article.reference_overview import ReferencesOverview


class ArticleStatistics(BaseModel):
    """The purpose of this class is to model the statistics
    the patron wants from the article endpoint

    We use BaseModel to avoid the cache attribute"""

    wari_id: str = ""
    lang: str = "en"  # language code according to Wikimedia
    page_id: int = 0  # page id of the Wikipedia in question
    references: Optional[ReferencesOverview] = None
    served_from_cache: bool = False
    site: str = "wikipedia"  # wikimedia site in question
    timestamp: int = 0  # timestamp at beginning of analysis
    isodate: str = ""  # isodate (human readable) at beginning of analysis
    timing: int = 0  # time to analyze in seconds
    title: str = ""

    class Config:  # dead: disable
        extra = Extra.forbid  # dead: disable