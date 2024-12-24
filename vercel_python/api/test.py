import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from custom_lib.automail_ai_craft import LinkedinWrapper, enrich_person
from dotenv import load_dotenv
import json

load_dotenv()

linkedin = LinkedinWrapper(os.getenv("LINKEDIN_USER"), os.getenv("LINKEDIN_PASS"), debug=True)

result = enrich_person(
        linkedin=linkedin,
        value="https://www.linkedin.com/in/ryan-hui-cfa-323a6529/",
        url_value=True
    )

print(json.dumps(result, indent=4))