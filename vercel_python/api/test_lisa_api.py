import sys
import os, requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from custom_lib.automail_ai_craft import LinkedinWrapper, enrich_person_more
from custom_lib.automail_ai_search_v2 import search_people
from custom_lib.cookies_extractor_async import cookie_extractor_from_json
from dotenv import load_dotenv
import json
import os
load_dotenv()

import time


res = requests.get(
        f'http://localhost:3000/chat/api/playwright' +
        f'?email={os.getenv("LINKEDIN_USER_OG")}&password={os.getenv("LINKEDIN_PASS_OG")}',
    )

json_data = res.json()
print(json.dumps(json_data['cookies'], indent=4))

if 'error' in json_data:
    print(False)
else:
    print(True)
    cookies_jar = cookie_extractor_from_json(json.loads(res.text)['cookies'])
    linkedin = LinkedinWrapper(os.getenv("LINKEDIN_USER"), os.getenv("LINKEDIN_PASS"), cookies=cookies_jar, debug=True)

    result = linkedin.search_people(
        keywords="investment banking",
        limit=10,
        offset=0
    )
    print(json.dumps(result, indent=4))

    time.sleep(20)

    result = linkedin.search_people(
        keywords="investment banking",
        limit=10,
        offset=0
    )
    print(json.dumps(result, indent=4))

    

# print(cookies_dict['cookies'])
# print(cookies_dict)
# cookies_jar = cookie_extractor_from_json(cookies_dict['cookies'])
# print(cookies_jar)

# linkedin = LinkedinWrapper(os.getenv("LINKEDIN_USER"), os.getenv("LINKEDIN_PASS"), cookies=cookies_jar, debug=True)

# result = linkedin.search_people(
#     keywords="investment banking",
#     limit=10,
#     offset=0
# )

# print(json.dumps(result, indent=4))