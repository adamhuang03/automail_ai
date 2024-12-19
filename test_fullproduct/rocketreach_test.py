import requests
from bs4 import BeautifulSoup
from linkedin_api.linkedin import default_evade 

def structure_rocketreach_query(input: str):
    # Fetch the page content
    return f"site:rocketreach.co {input} email format"

def get_first_google_result_link(query):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/70.0.3538.77 Safari/537.36"
        )
    }

    search_url = "https://www.google.com/search"
    params = {"q": query, "num": "10"}

    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} from Google.")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    link_tags = soup.select('a[href^="/url?"][href*="https://rocketreach.co/"]')
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
    

def get_top_email_format(url):
    # Fetch the page content
    default_evade()
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
    response = requests.get(url, headers=headers_firefox)
    # print(response.status_code, response.headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locate the table containing the email formats
    # According to the provided HTML, the table is inside a div with class 'table-wpr'
    # We'll find the first table row after the thead, which should represent the most common pattern.
    table_wpr = soup.find('div', class_='table-wpr')
    if not table_wpr:
        return None

    # Find the first row inside the table body
    table = table_wpr.find('table', class_='table')
    if not table:
        return None
    
    tbody = table.find('tbody')
    if not tbody:
        return None
    
    first_row = tbody.find('tr')
    if not first_row:
        return None

    # Extract pattern and example from the first row
    cells = first_row.find_all('td')
    if len(cells) < 2:
        return None
    
    pattern = cells[0].get_text(strip=True)
    example = cells[1].get_text(strip=True)
    
    return pattern, example

# Example usage:

if __name__ == "__main__":
    # Example search
    input_companies = [
        # "Moelis",
        # "Morgan Stanley",
        # "GitHub",
        # "Google",
        # "Microsoft",
        # "Apple",
        "Facebook",
        "Twitter",
        # "Amazon",
        # "Tesla",
        # "Netflix",
        # "Spotify",
        # "Airbnb",
        # "Uber",
        # "Lyft",
        # "Snapchat",
        # "Instagram",
        # "TikTok",
        # "Pinterest",
        # "Reddit",
    ]
    for company in input_companies:
        query = structure_rocketreach_query(company)
        first_link = get_first_google_result_link(query)
        if first_link:
            print("First link found:", first_link)
            result = get_top_email_format(first_link)
            if result:
                pattern, example = result
                print(f"For URL: {first_link}")
                print(f"Top Email Format Pattern: {pattern}")
                print(f"Example: {example}")
                print("-" * 50)
            else:
                print("Could not find format for", first_link)
        else:
            print("No link found.")
    
    # urls = [
    #     "https://rocketreach.co/moelis-company-email-format_b5c01de7f42e0fcd",
    #     "https://rocketreach.co/morgan-stanley-email-format_b5c18cabf42e08c4",
    #     "https://rocketreach.co/github-email-format_b5d3bf8bf42e46c1"
    # ]

    # for url in urls:
    #     result = get_top_email_format(url)
    #     if result:
    #         pattern, example = result
    #         print(f"For URL: {url}")
    #         print(f"Top Email Format Pattern: {pattern}")
    #         print(f"Example: {example}")
    #         print("-" * 50)
    #     else:
    #         print(f"Could not find format for {url}")
