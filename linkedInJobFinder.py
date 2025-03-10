from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import http.client
import json
import credentials
from llm import llmJobRelevanceCheckForLinkedIn
from typing import List

"""
1) Before running this file kindly create credential.py file (as I didn't push my keys to github)
    Inside create

    LinkedInScrapper_api_key= "" 
    You can get this key for free :) from https://rapidapi.com/fantastic-jobs-fantastic-jobs-default/api/linkedin-job-search-api


    groq_api_key = ""
    This we can easily also get from GroqCloud from free.

2) Then run this file by
    uvicorn linkedInJobFinder:app --reload


3) Test API Locally on your browser by
    http://127.0.0.1:8000/docs
    And using endpoint /get-relevant-jobs/


"""

app = FastAPI()

class UserChoices(BaseModel):
    Title_Of_The_Job: str
    Experience: str
    Salary: str
    Job_Nature: str  # On-site, Hybrid, Remote
    Location: str
    Skills: str

@app.get("/")
def root():
    return {"message": "Welcome to LinkedIn Job Finder API! Use /get-relevant-jobs/ to search for jobs."}

@app.post("/get-relevant-jobs/")
def get_relevant_jobs(userChoicesDict: UserChoices):
    conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': credentials.LinkedInScrapper_api_key,
        'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
    }

    title_filter = userChoicesDict.Title_Of_The_Job.replace(" ", "%20")
    location_filter = userChoicesDict.Location.replace(" ", "%20")
    ai_work_arrangement_filter = userChoicesDict.Job_Nature

    filterThatUserSelect = f"/active-jb-7d?title_filter={title_filter}&location_filter={location_filter}&ai_work_arrangement_filter={ai_work_arrangement_filter}"

    try:
        conn.request("GET", filterThatUserSelect, headers=headers)
        res = conn.getresponse()
        data = res.read()
    except Exception as e:
        print(f"API connection error: {e}")
        raise HTTPException(status_code=502, detail="Failed to connect to job search API.")
    finally:
        conn.close()

    try:
        parsed_data = json.loads(data.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse job API response.")

    relevent_Jobs = []

    if isinstance(parsed_data, list) and parsed_data:
        userChoicesFormatted = {
            "Title Of The Job": userChoicesDict.Title_Of_The_Job,
            "Experience you have(for example 0-2, 2-5 etc)": userChoicesDict.Experience,
            "Salary": userChoicesDict.Salary,
            "the job Nature, use the specified keys(On-site, Hybrid, Remote)": userChoicesDict.Job_Nature,
            "your location": userChoicesDict.Location,
            "Skills": userChoicesDict.Skills
        }

        for job in parsed_data:
            if llmJobRelevanceCheckForLinkedIn(userChoicesFormatted, job):
                relevent_Jobs.append(job)

        if not relevent_Jobs:
            return {"message": "No relevant jobs found.", "relevant_jobs": []}
    else:
        raise HTTPException(status_code=404, detail="No jobs found matching your criteria.")

    return {"relevant_jobs": relevent_Jobs}
