import sys
import os, requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from custom_lib.automail_ai_craft import LinkedinWrapper, enrich_person_more
from custom_lib.automail_ai_search_v2 import search_people
from dotenv import load_dotenv
import json

load_dotenv()

res = requests.get('http://localhost:3000/chat/api/playwright')
print(res.content)