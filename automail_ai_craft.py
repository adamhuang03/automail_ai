import keyword
from re import search
from turtle import pu
from typing import List, Tuple, Optional

from httpx import Limits
from sqlalchemy import true
from sqlalchemy.engine import result
from lib.linkedin_wrapper import LinkedinWrapper
import math
import logging
import traceback
import json
import pandas as pd
import os
from openai import OpenAI
from dataclasses import dataclass, asdict
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from prompt import OPENAI_EXTRACTION_PROMPT, POST_PROMPT_INSTR, EMAIL_SYSTEM_PROMPT, EMAIL_TEMPLATE

# function to enrich each person in a json, toggle for urn_id or url
def enrich_person(
    linkedin: LinkedinWrapper,
    value: str,
    url_value: bool = False
) -> dict:
    logger.info("Starting profile enrichment for value: %s (url_value=%s)", value, url_value)
    
    # Create a cleaned person dictionary with relevant fields
    if url_value:
        url = value.split('?')[0].rstrip('/')
        id = url.split('/')[-1]
        logger.info("Extracting profile using public_id: %s", id)
    else:
        id = value
        logger.info("Extracting profile using urn_id: %s", value)
    
    person = linkedin.get_profile(id)

    if not person:
        logger.warning("No profile data returned for value: %s", value)
        return {}
    
    logger.info("Successfully retrieved profile for %s %s", 
                person.get("firstName", "Unknown"), 
                person.get("lastName", "Unknown"))
    
    cleaned_person = {
        "personal": {
            "first_name": person.get("firstName"),
            "last_name": person.get("lastName"),
            "headline": person.get("headline"),
            "location": person.get("locationName"),
            "city": person.get("geoLocationName"),
            "industry": person.get("industryName")
        },
        "experiences": [],
        "education": []
    }
    
    # Add experiences
    experience_count = len(person.get("experience", []))
    logger.info("Processing %d experiences", experience_count)
    for exp in person.get("experience", []):
        cleaned_exp = {
            "title": exp.get("title"),
            "company": exp.get("companyName"),
            "description": exp.get("description"),
            "start_date": exp.get("startDate"),
            "end_date": exp.get("endDate")
        }
        cleaned_person["experiences"].append(cleaned_exp)
    
    # Add education
    education_count = len(person.get("education", []))
    logger.info("Processing %d education entries", education_count)
    for edu in person.get("education", []):
        cleaned_edu = {
            "school": edu.get("schoolName"),
            "activities": edu.get("activities"),
            "grade": edu.get("grade"),
            "start_date": edu.get("timePeriod", {}).get("startDate"),
            "end_date": edu.get("timePeriod", {}).get("endDate")
        }
        cleaned_person["education"].append(cleaned_edu)
    
    # Add identifier based on parameter
    if url_value:
        cleaned_person["id"] = person.get("public_id")
        logger.info("Added public_id to profile")
    else:
        cleaned_person["id"] = person.get("profile_urn")
        logger.info("Added profile_urn to profile")
    
    logger.info("Successfully enriched profile data")
    return cleaned_person

def multi_enrich_persons(
    linkedin: LinkedinWrapper,
    values: List[str],
    url_value: bool = False
) -> List[dict]:
    return [enrich_person(linkedin, value, url_value) for value in values]

def draft_email(
    openai: OpenAI,
    user_profile: dict,
    candidate_profile: dict,
    keyword_industry: str
) -> str:
    messages = [
        {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
        {"role": "user", "content": f"""
                User Profile:
        {json.dumps(user_profile, indent=2)}

        Candidate Profile:
        {json.dumps(candidate_profile, indent=2)}

        Num: 1
        Role:
        Email template:
        {EMAIL_TEMPLATE}
        """}
    ]
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content  


if __name__ == "__main__":

    import json, os
    from pprint import pprint

    from dotenv import load_dotenv
    load_dotenv()
    openai = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    linkedin_user = os.getenv("LINKEDIN_USER")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")
    linkedin = LinkedinWrapper(linkedin_user, linkedin_password, debug=True)

    # ==================================================================
    # Single enrichement

    # result = enrich_person(
    #     linkedin=linkedin,
    #     value="https://www.linkedin.com/in/vaishika-mathisayan/?originalSubdomain=ca",
    #     url_value=True
    # )

    # with open("data/user_profile_vaishika.json", "w") as f:
    #     import json
    #     json.dump(result, f, indent=4)

    # with open("data/user_profile_hasan.json", "r") as f:
    #     user_profile = json.load(f)
    
    # email = draft_email(
    #     openai=openai,
    #     user_profile=user_profile,
    #     candidate_profile=result
    # )

    # print("\nGenerated Email:")
    # print(email)
    
    # ==================================================================
    # Multi enrichement

    # Read csv
    csv_file = "v2_output/linkedin_data.csv"
    with open(csv_file, "r") as f:
        csv_data = [line.strip().split(",") for line in f.readlines()]
    # Get the 1st column
    list_of_urns = [row[0] for row in csv_data]
    
    multi_result_enriched = multi_enrich_persons(
        linkedin=linkedin,
        values=list_of_urns,
        url_value=False
    )

    with open("data/user_profile_vaishika.json", "r") as f:
        user_profile = json.load(f)

    with open("v2_search/params.json", "r") as f:
        params = json.load(f)
        keyword_industry = params["keyword_industry"]

    emails = []
    
    for enriched_person in multi_result_enriched:
        email = draft_email(
            openai=openai,
            user_profile=user_profile,
            candidate_profile=enriched_person,
            keyword_industry=keyword_industry
        )
        emails.append(email)

    # Add the enriched data to the csv data
    for i in range(len(csv_data)):
        csv_data[i].append(json.dumps(emails[i]))
    
    # Save the csv data
    with open("v2_output/linkedin_data_w_enriched.csv", "w") as f:
        f.write("urn_id,url,email\n")
        f.write("\n".join([",".join(row) for row in csv_data]))


    # ==================================================================
