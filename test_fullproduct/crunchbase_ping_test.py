import requests

# # Define the URL
# url = "https://www.crunchbase.com/organization/homebase"

# # Define the headers
# headers = {
#     # "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#     "accept-encoding": "gzip, deflate, br, zstd",
#     "accept-language": "en-US,en;q=0.9",
#     "cache-control": "max-age=0",
#     "cookie": "cb_analytics_consent=granted; cid=CigQZ2dYqOmoaQAWD0vxAg==; featureFlagOverride=%7B%7D; __cflb=02DiuJLCopmWEhtqNz3x2VesGhPn4wGcJcgi5GVtXAogG; trustcookie=eyJraWQiOiJjcnVuY2hiYXNlIiwiYWxnIjoiUlMyNTYifQ.eyJqdGkiOiI4ZGQyZmQzNC00MzVhLTRjYmItODM5Yy0wMTliYjg4ZWM0ODIiLCJpc3MiOiJ1c2Vyc2VydmljZV85NGU0NDA4M18xIiwic3ViIjoiNzU4YTE5OWMtMThlNS00ZGFlLWExNjUtOGYwM2Q5MDEyYjRlIiwiZXhwIjoxNzM2MTE2MTk3LCJpYXQiOjE3MzYwMjk3OTcsInNjciI6MH0.oYj2JvJjb7TLraN5ycAHkuVBhuuZYlszqjU518KGRjGdz_l-XWYrd8JI30sEXurljJZWfAYmHSEces8mLftcXgG2th7wmtdjS3m0F65EPtP2Zt1FOhVDrSm_r5WFteY0OBck6xGIqguhf2CXZ52lGdQwlRpVJEJT2pEcUyxzDMiwZg1c6VWVRL2P6cS5UtLF7xsQYoiWRl-nGl-POFcLdNXRwANVt-T-IvUkWKkwO3b0B3NLXG5LIbdxRO6yIj0aA0sAeNxMrOhi3q8-LWYwBVgUDnqAKrvNYaodL1lYH0MkKgiGGK1cTH18zBJoymwGT-cLntayAwwKiacJC1-WKA; __cf_bm=.Js5mGkAEUtdTyZ7KLXJgfyMtF_tGMtB1R3lmj45Jck-1736034247-1.0.1.1-J9TTjgmfoJwPp3gHGYbsN.r8r3eDU8thNJ_2HI_zhdW8xN8672KVkewbauCEnctW3G4tKFQ19ywcLCjuDsy69Q; cf_clearance=UbpB3nQCUDYPMRZ5u7x3w.aVKBfEJNROzkDbJqIWx.4-1736034607-1.2.1.1-M1Oy0hedtH2SUGag2.lIiWaFj1kSQtQgcegtmYKf36M03iRKCLOf0RlgZDYCs0tFG5nCVoMvpZRs9eWUFdozKBy..hwUqocTxSafpMGjyJJ0XMAinhcGu_WjcHofrD5IFBww.cKEQqrgJOoZQSIrfruwOaCTyVIM6Yg6JwKU0GQlpxEDCyLus8DFi30E3QbthdGMzLgquv9kLPCY1XGmFIBoDaf26YQT8kZK4vPRRrcvsUBocH010S.OgkaOEKSMEuVclF95vxQsNH5XJFjPfa92HUn0j0FcaFZv4UVMSjt5hUkwnN7s4GwGGzsE.pA0yG17DyZ_CxfPdb2JoTgBAD5OgZ0cy5o0GqOUX2fpxX2dbj6xalQGA7xRJN7ui9U48bvgrBbnqi0QnMxEX6b6USdFMexzSf4mUv0GAWBtVxw; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Jan+04+2025+18%3A52%3A17+GMT-0500+(Eastern+Standard+Time)&version=202304.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&AwaitingReconsent=false",
#     "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
#         "sec-ch-ua-mobile": "?0",
#         "sec-ch-ua-platform": '"Windows"',
#         "sec-fetch-dest": "document",
#         "sec-fetch-mode": "navigate",
#         "sec-fetch-site": "same-origin",
#         "sec-fetch-user": "?1",
#         "upgrade-insecure-requests": "1",
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
# }

# # Make the GET request
# response = requests.get(url, headers=headers)

# # Output the response
# print(response.status_code)
# print(response.headers)
# print(response.content)


# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

# chrome_options = Options()
# chrome_options.add_argument("--headless")

# driver = webdriver.Chrome(options=chrome_options)

# # Navigate to the page
# driver.get("https://www.crunchbase.com/organization/homebase")

# # Grab the page source
# html = driver.page_source
# print(html)

# driver.quit()

url = 'https://automail-ai-apple.vercel.app'

def test_api_call(url, linkedin_url):
    endpoint = f"{url}/selenium"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "linkedin_url": linkedin_url
    }
    
    response = requests.post(
        endpoint,
        headers=headers,
        json=payload
    )
    
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.json()

if __name__ == "__main__":
    linkedin_url = "https://www.crunchbase.com/organization/homebase"
    
    try:
        result = test_api_call(url, linkedin_url)
        print("Response:", result)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
