from re import search
from typing import List, Tuple, Optional

from httpx import Limits
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

from prompt import OPENAI_EXTRACTION_PROMPT, POST_PROMPT_INSTR

# function to enrich each person in a json, toggle for urn_id or url
def enrich_person(person: dict, urn_id: bool = True) -> dict:
    if urn_id:
        person["urn_id"] = person.pop("urn")
    else:
        person["url"] = person.pop("url")
    return person   



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

    
    # ==================================================================

    
    # ==================================================================

    
