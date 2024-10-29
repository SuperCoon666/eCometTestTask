from pydantic import BaseModel
from typing import List
from datetime import date


class RepoInfo(BaseModel):
    repo: str
    owner: str
    position_cur: int
    position_prev: int
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: str


class RepoActivity(BaseModel):
    date: date
    commits: int
    authors: List[str]
