import http.client
import json
import credentials

#To run the script as you dont have the credentials.py(which contain the api key) so kindly comment it
#and get the key from the link described below




conn = http.client.HTTPSConnection("linkedin-job-search-api.p.rapidapi.com")
headers = {
    # I didnt push the api key but you can get a new rapid api key from the below link for free :)
    # https://rapidapi.com/fantastic-jobs-fantastic-jobs-default/api/linkedin-job-search-api
    'x-rapidapi-key': credentials.api_key,
    'x-rapidapi-host': "linkedin-job-search-api.p.rapidapi.com"
}
# userChoicesDict = {
#     "Title Of The Job": "",
#     "Experience you have(for example 0-2, 2-5 etc)": "",
#     "Salary": "",
#     "the job Nature, use the specified keys(On-site, Hybrid, Remote)": "",
#     "your location": "",
#     "Skills": ""
# }








# #Asking User's about his or her prefrences
# for userChoice in userChoicesDict:
#     userChoicesDict[userChoice] = input(f"Enter {userChoice}: ")

# #URL Encoding for vars that may have have spaces and are sent to api to get the results 
# title_filter = userChoicesDict["Title Of The Job"].replace(" ", "%20")
# location_filter = userChoicesDict["your location"].replace(" " , "%20")
# ai_work_arrangement_filter = userChoicesDict["the job Nature, use the specified keys(On-site, Hybrid, Remote)"]

#print (title_filter)

#filterThatUserSelect = f"/active-jb-7d?title_filter={title_filter}&location_filter={location_filter}&ai_work_arrangement_filter={ai_work_arrangement_filter}"
# filterThatUserSelect = "/active-jb-24h?title_filter=Python%20Developer"




#print(filterThatUserSelect)
#print(userChoicesDict)



conn.request("GET", "/active-jb-7d?title_filter=Devops%20Engineer&location_filter=Islamabad%20Pakistan&ai_work_arrangement_filter=On-site", headers=headers)

res = conn.getresponse()
data = res.read()

parsed_data = json.loads(data.decode("utf-8"))


print(parsed_data)

# for index, obj in enumerate(parsed_data):
#     print(f"Object {index + 1}:")
#     print(json.dumps(obj, indent=4))  # Pretty-print JSON object
#     print("-" * 40)  # Separator line







# Pretty-print the JSON
#print(json.dumps(parsed_data, indent=4))