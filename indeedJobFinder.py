from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import requests
from groq import Groq
from typing import Optional, List, Dict, Any
import credentials
from llm import llmJobRelevanceCheckForIndeed
from DataHolderForIndeed import UserPreferences , JobSearchParams
# Create FastAPI instance
app = FastAPI()



class JobRequest(BaseModel):
    job_search_params: JobSearchParams
    user_preferences: UserPreferences

def fetch_jobs(params: JobSearchParams):
    url = "https://indeed-scraper-api.p.rapidapi.com/api/job"
    scraper = {"query": params.query, "maxRows": params.max_rows}
    
    if params.location:
        scraper["location"] = params.location
    if params.job_type:
        scraper["jobType"] = params.job_type
    if params.level:
        scraper["level"] = params.level
    if params.radius:
        scraper["radius"] = params.radius
    if params.sort:
        scraper["sort"] = params.sort
    if params.from_days:
        scraper["fromDays"] = params.from_days
    if params.remote:
        scraper["remote"] = params.remote
    if params.country:
        scraper["country"] = params.country

    headers = {
        "x-rapidapi-key": credentials.IndeedScrapper_api_key,
        "x-rapidapi-host": "indeed-scraper-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json={"scraper": scraper}, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")

def extract_job_details(job: Dict[str, Any]) -> Dict[str, Any]:
    salary_info = job.get("salary", {})
    location_info = job.get("location", {})
    company_rating = job.get("rating", {}).get("rating", "Not rated")
    
    requirements = []
    for req in job.get("requirements", []):
        severity = "Required" if req.get("requirementSeverity") == "REQUIRED" else "Preferred"
        requirements.append(f"{severity}: {req.get('label')}")

    return {
        "id": job.get("id"),
        "title": job.get("title", ""),
        "company": job.get("companyName", "Company not specified"),
        "rating": company_rating,
        "location": location_info.get("formattedAddressShort", "Location not specified"),
        "salary": salary_info.get("salaryText", "Not specified"),
        "salary_range": f"{salary_info.get('salaryMin')}-{salary_info.get('salaryMax')} ({salary_info.get('salaryType')})"
        if salary_info.get('salaryMin') and salary_info.get('salaryMax') else "Not specified",
        "is_remote": job.get("isRemote", False),
        "job_type": job.get("jobType", []),
        "benefits": job.get("benefits", []),
        "requirements": requirements[:3],
        "urgent_hire": job.get("hiringDemand", {}).get("isUrgentHire", False),
        "posted": job.get("age", ""),
        "url": job.get("jobUrl", ""),
        "apply_url": job.get("applyUrl", "")
    }


@app.post("/rank-jobs")
async def rank_jobs(request: JobRequest):
    api_response = fetch_jobs(request.job_search_params)
    
    if "returnvalue" not in api_response or "data" not in api_response["returnvalue"]:
        raise HTTPException(status_code=500, detail="Invalid API response format")
    
    raw_jobs = api_response["returnvalue"]["data"]
    if not raw_jobs:
        return {"message": "No jobs found", "jobs": []}
    
    jobs = [extract_job_details(job) for job in raw_jobs]
    
    if not any(request.user_preferences.dict().values()):
        return {"jobs": jobs}
    
    ranked = llmJobRelevanceCheckForIndeed(jobs, request.user_preferences)
    job_map = {job["id"]: job for job in jobs}
    
    ranked_jobs = []
    for entry in ranked.get("rankings", []):
        job = job_map.get(entry["id"])
        if job:
            job.update({"score": entry["score"], "explanation": entry["explanation"]})
            ranked_jobs.append(job)
    
    return {"jobs": ranked_jobs}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)