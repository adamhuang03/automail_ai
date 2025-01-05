import requests, json, time
from bs4 import BeautifulSoup
from linkedin_api.linkedin import default_evade 

def structure_crunchbase_query(company: str):
    # Fetch the page content
    return f"site:crunchbase.com/organization {company}"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/70.0.3538.77 Safari/537.36"
    )
}
headers_firefox = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) "
        "Gecko/20100101 Firefox/120.0"
    )
}
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}

headers_more_real = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1'
}

def get_first_google_result_link(query):

    search_url = "https://www.google.com/search"
    params = {"q": query, "num": "10"}

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} from Google.")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    link_tags = soup.select('a[href^="/url?"][href*="https://www.crunchbase.com/organization"]')
    link = link_tags[0]['href'].split('url=')[1].split('&')[0]
    
    default_evade()
    
    if link:
        return link
    return None


    # # Save the search results as a clean JSON
    # with open('google_search_results.html', 'w') as f:
    #     f.write(soup.prettify())


    # # First find the search container
    # search_div = soup.find('div', id='search')
    # if not search_div:
    #     print("No search results container found.")
    #     return None

    # # Inside it, find the first 'div.yuRUbf > a'
    # link_tag = search_div.select_one('div.yuRUbf > a')
    # if link_tag and link_tag.has_attr('href'):
    #     return link_tag['href']

    # print("No link found in the search results.")


def get_company_description_box(crunchbase_url):
    # Call function only if no supabase
    # Fetch the page content
    default_evade()
    
    # url = "https://api.scrapingant.com/v2/general"
    # params = {
    #     "url": crunchbase_url,
    #     "x-api-key": "662456c077a34243875bff69fa8cbfde"
    # }

    # print(url, params)
    # response = requests.get(url, params=params)
    # response.raise_for_status()

    # soup = BeautifulSoup(response.text, 'html.parser')
    
    # with open('crunchbase_page.txt', 'w') as f:
    #     f.write(response.text)

    with open('crunchbase_page.txt', 'r') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the profile-section element
    profile_section = soup.find('profile-section')
    # if not profile_section:
    #     return None

    # # Find the section-card within the profile-section
    # section_card = profile_section.find('section-card')
    # if not section_card:
    #     return None
    
    # # Extract the text content from the section-card
    # description = section_card.get_text(strip=True)
    # if not description:
    #     return None
    
    return profile_section

# Example usage:

if __name__ == "__main__":
    # # Example search
    # input_companies = [
    #     # "Moelis",
    #     # "Morgan Stanley",
    #     # "GitHub",
    #     # "Google",
    #     # "Microsoft",
    #     # "Apple",
    #     # "Facebook",
    #     # "Twitter",
    #     # "Homebase",
    #     # "Amazon",
    #     "Tesla",
    #     # "Netflix",
    #     # "Spotify",
    #     # "Airbnb",
    #     # "Uber",
    #     # "Lyft",
    #     # "Snapchat",
    #     # "Instagram",
    #     # "TikTok",
    #     # "Pinterest",
    #     # "Reddit",
    # ]
    # for company in input_companies:
    #     start_time = time.time()
    #     query = structure_crunchbase_query(company)
    #     first_link = get_first_google_result_link(query)
    #     if first_link:
    #         print("First link found:", first_link)
    #         result = get_company_description_box(first_link)
    #         end_time = time.time()
    #         duration_seconds = end_time - start_time
    #         print("Duraction:", duration_seconds)
    #         if result:
    #             print(f"For URL: {first_link}")
    #             print(f"Company Description: {result}")
    #             print("-" * 50)
    #         else:
    #             print("Could not find description for", first_link)
    #     else:
    #         print("No link found.")

    result = get_company_description_box("")
    print(result)
