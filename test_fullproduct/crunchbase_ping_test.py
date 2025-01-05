import requests, time

url = "https://api.scrapingant.com/v2/general"
params = {
    "url": "https://www.crunchbase.com/organization/homebase",
    "x-api-key": "662456c077a34243875bff69fa8cbfde"
}

start_time = time.time()
try:
    response = requests.get(url, params=params)
    # response.raise_for_status()  # Raises an exception for error status codes
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")    
end_time = time.time()
duration_seconds = end_time - start_time
with open('crunchbase_homebase.txt', 'w') as f:
    f.write(response.text)
print(response.text, duration_seconds)