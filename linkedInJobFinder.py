import http.client
import json
import credentials
from llm import llmJobRelevanceCheckForLinkedIn



#To run the script as you dont have the credentials.py(which contain the api keys) so kindly comment it
#and get the key from the link described below




conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")
headers = {
    # I didnt push the api key but you can get a new rapid api key from the below link for free :)
    # https://rapidapi.com/fantastic-jobs-fantastic-jobs-default/api/linkedin-job-search-api
    'x-rapidapi-key': credentials.api_key,
    'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
}
userChoicesDict = {
    "Title Of The Job": "",
    "Experience you have(for example 0-2, 2-5 etc)": "",
    "Salary": "",
    "the job Nature, use the specified keys(On-site, Hybrid, Remote)": "",
    "your location": "",
    "Skills": ""
}








#Asking User's about his or her prefrences
for userChoice in userChoicesDict:
    userChoicesDict[userChoice] = input(f"Enter {userChoice}: ")

#URL Encoding for vars that may have have spaces and are sent to api to get the results 
title_filter = userChoicesDict["Title Of The Job"].replace(" ", "%20")
location_filter = userChoicesDict["your location"].replace(" " , "%20")
ai_work_arrangement_filter = userChoicesDict["the job Nature, use the specified keys(On-site, Hybrid, Remote)"]

#print (title_filter)

filterThatUserSelect = f"/active-jb-7d?title_filter={title_filter}&location_filter={location_filter}&ai_work_arrangement_filter={ai_work_arrangement_filter}"
# filterThatUserSelect = "/active-jb-24h?title_filter=Python%20Developer"




#print(filterThatUserSelect)
#print(userChoicesDict)



# conn.request("GET",filterThatUserSelect, headers=headers)

# res = conn.getresponse()
# data = res.read()

# parsed_data = json.loads(data.decode("utf-8"))


# whichJobIsReleventOrNot = [0] * len(parsed_data)




# for job in parsed_data:
#     print(f"\n--- Job: {job.get('title', 'No Title')} ---")
#     print(json.dumps(job, indent=4))
#     print("-" * 30)


conn.request("GET",filterThatUserSelect, headers=headers)

res = conn.getresponse()
data = res.read()
decoded_data = data.decode("utf-8")
relevent_Jobs = []
try:
    parsed_data = json.loads(decoded_data)
    print(f"Response type: {type(parsed_data)}")
    print(f"Total jobs found: {len(parsed_data) if isinstance(parsed_data, list) else 'Not a list'}")
    
    # If it's a list with content, process each job
    if isinstance(parsed_data, list) and parsed_data:
        relevant_count = 0
        
        print("\nAnalyzing job relevance with AI, focusing on skills match...\n")
        
        for index, job in enumerate(parsed_data):
            print(f"Checking job {index+1}/{len(parsed_data)}: {job.get('title', 'No Title')}...")
            
            # Use LLM to check if this job is relevant to user preferences with focus on skills
            is_relevant = llmJobRelevanceCheckForLinkedIn(userChoicesDict, job)
            relevent_Jobs.append(job)
            if is_relevant:
                relevant_count += 1
                print(f"\n--- RELEVANT JOB {relevant_count}: {job.get('title', 'No Title')} ---")
                print(f"Company: {job.get('organization', 'N/A')}")
                print(f"Location: {', '.join(job.get('locations_derived', ['N/A']))}")
                print(f"URL: {job.get('url', 'N/A')}")
                
                # Print skills match information
                print("\nPotential Skills Match:")
                org_specialties = job.get('linkedin_org_specialties', [])
                if org_specialties:
                    print("Organization specialties: " + ", ".join(org_specialties))
                    
                print("-" * 30)
                
                # Optionally print the full job details 
                # Uncomment the line below if you want to see all job details
                # print(json.dumps(job, indent=4))
        
        print(f"\nFound {relevant_count} relevant jobs out of {len(parsed_data)} total jobs.")
    else:
        print("No jobs found in the response or response format is not a list.")
        print("Actual response content:")
        print(json.dumps(parsed_data, indent=4))
        
except json.JSONDecodeError as e:
    print(f"Could not parse JSON: {e}")


print(relevent_Jobs)