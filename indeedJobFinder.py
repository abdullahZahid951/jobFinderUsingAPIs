from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import credentials
import json

app = FastAPI()

# Define request body schema
class JobSearchRequest(BaseModel):
    query: str
    location: str
    jobType: str
    radius: str
    fromDays: str
    country: str

# Replace this with your actual API key
RAPIDAPI_KEY = credentials.IndeedScrapper_api_key

@app.post("/search_jobs")
def search_jobs(job_request: JobSearchRequest):
    url = "https://indeed-scraper-api.p.rapidapi.com/api/job"

    # Payload with user-provided and hardcoded values
    payload = {
        "scraper": {
            "maxRows": 15,  # Hardcoded
            "query": job_request.query,
            "location": job_request.location,
            "jobType": job_request.jobType,
            "radius": job_request.radius,
            "sort": "relevance",  # Hardcoded
            "fromDays": job_request.fromDays,
            "country": job_request.country
        }
    }

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "indeed-scraper-api.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    # Make the request
    response = requests.post(url, json=payload, headers=headers)

    # Handle possible errors
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    # The response comes as a stringified JSON in 'detail'
    try:
        response_data = response.json()
        # 'detail' contains a string JSON, parse it
        detail_data = json.loads(response_data.get("detail", "{}"))
        returnvalue = detail_data.get("returnvalue", {})
        jobs_data = returnvalue.get("data", [])

        # Return only jobs list
        return {"jobs": jobs_data}

    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse API response: {str(e)}")
