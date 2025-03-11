from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class UserPreferences(BaseModel):
    skills: List[str] = []
    experience_years: Optional[int] = None
    remote_preference: Optional[str] = None
    min_salary: Optional[int] = None
    company_size: Optional[str] = None
    important_benefits: List[str] = []



class JobSearchParams(BaseModel):
    query: str
    location: Optional[str] = ""
    job_type: Optional[str] = None
    level: Optional[str] = None
    radius: Optional[str] = None
    sort: Optional[str] = None
    from_days: Optional[str] = None
    remote: Optional[str] = None
    country: Optional[str] = "us"
    max_rows: Optional[int] = 20
