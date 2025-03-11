from groq import Groq
from fastapi import FastAPI, HTTPException
from typing import Optional, List, Dict, Any
from DataHolderForIndeed import UserPreferences


import json
import credentials
def llmJobRelevanceCheckForLinkedIn(user_preferences, job_data):
    client = Groq(
        api_key=credentials.groq_api_key,
    )

    # Extract job description from organization description or specialties
    job_description = job_data.get('linkedin_org_description', '')
    if not job_description and 'linkedin_org_specialties' in job_data:
        job_description = ", ".join(job_data.get('linkedin_org_specialties', []))

    # Add a leniency message for LLM prompt
    leniency_instruction = """
    Note: Be lenient in matching. If most important fields like 'Skills' match, but other preferences like salary, experience, or job nature are missing or unclear, still consider it relevant.
    """

    # Create a prompt that asks the LLM to analyze if the job matches user preferences with focus on skills and leniency
    prompt = f"""
    I need to determine if this job posting matches the user's preferences, with special attention to the skills match. 

    USER PREFERENCES (Treat 'Any' as no specific preference):
    - Job Title: {user_preferences['Title Of The Job']}
    - Experience Level: {user_preferences['Experience you have(for example 0-2, 2-5 etc)']}
    - Desired Salary: {user_preferences['Salary']}
    - Work Arrangement: {user_preferences['the job Nature, use the specified keys(On-site, Hybrid, Remote)']}
    - Location: {user_preferences['your location']}
    - Skills: {user_preferences['Skills']}

    JOB POSTING:
    - Title: {job_data.get('title', 'N/A')}
    - Organization: {job_data.get('organization', 'N/A')}
    - Location: {', '.join(job_data.get('locations_derived', ['N/A']))}
    - Remote Status: {job_data.get('remote_derived', 'N/A')}
    - Employment Type: {', '.join(job_data.get('employment_type', ['N/A']))}
    - Seniority: {job_data.get('seniority', 'N/A')}
    - Organization Industry: {job_data.get('linkedin_org_industry', 'N/A')}
    - Organization Specialties: {', '.join(job_data.get('linkedin_org_specialties', ['N/A']))}

    JOB DESCRIPTION:
    {job_description}

    {leniency_instruction}

    Carefully analyze if the user's **Skills** match with the job description, title, and organization specialties. The skills match is the **most important factor**. Other preferences are secondary and flexible. 
    If skills match and overall it looks suitable, return "True". If not, return "False". No explanation needed.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            stream=False,
        )
        response = chat_completion.choices[0].message.content.strip()
        return "True" in response 
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return True 
    




def llmJobRelevanceCheckForIndeed(jobs: List[Dict], preferences: UserPreferences) -> Dict:
    groq_client = Groq(api_key=credentials.groq_api_key)
    
    prompt = f"""
    User preferences:
    {json.dumps(preferences.dict(), indent=2)}
    
    Job listings:
    {json.dumps(jobs, indent=2)}
    
    Score each job 0-100 based on preference matching. Consider skills, experience, salary, remote preference, location, company size, benefits, and responsibilities.
    
    Return JSON with rankings containing id, score, and explanation. Sort by score descending.
    """
    
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing failed: {str(e)}")
