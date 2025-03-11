# 🔑 Setup Guide for Job Finder APIs

##  Create `credentials.py`

Before running the project, you **must create a file named `credentials.py`** in the root directory.

Add the following keys inside the file:

```python
# credentials.py

# Get from https://rapidapi.com/fantastic-jobs-fantastic-jobs-default/api/linkedin-job-search-api
LinkedInScrapper_api_key = ""

# Get from https://console.groq.com/keys
groq_api_key = ""

# Get from https://rapidapi.com/border-line-border-line-default/api/indeed-scraper-api
IndeedScrapper_api_key = ""

```
# After This Run Files With
```python
uvicorn linkedInJobFinder:app --reload
uvicorn indeedJobFinder:app --reload
```
