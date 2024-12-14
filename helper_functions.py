from lib.linkedin_wrapper import LinkedinWrapper
from linkedin_api.utils.helpers import get_id_from_urn, get_urn_from_raw_update
import json
import logging
import traceback
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_company(linkedin: LinkedinWrapper, public_id: str) -> Dict:
    """
    Retrieve company information and URN ID from LinkedIn
    Args:
        linkedin: LinkedinWrapper instance
        public_id: Company's public ID
    Returns:
        Dict containing either company URN ID or error information
    """
    try:
        logger.info(f"Retrieving company information for public_id: {public_id}")
        company = linkedin.get_company(public_id=public_id)
        urn_id = get_id_from_urn(company['entityUrn'])
        result = {
            "success": True,
            "company_urn_id": urn_id,
            "timestamp": "2024-12-10T22:07:56-05:00",
            "public_id": public_id
        }
    except Exception as e:
        logger.error(f"Error retrieving company information: {str(e)}")
        result = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "error_traceback": traceback.format_exc(),
            "timestamp": "2024-12-10T22:07:56-05:00",
            "public_id": public_id
        }
    
    with open("v2_search/input/company.json", "w") as f:
        json.dump(result, f, indent=4)
    return result

def get_school(linkedin: LinkedinWrapper, public_id: str) -> Dict:
    """
    Retrieve school information and URN ID from LinkedIn
    Args:
        linkedin: LinkedinWrapper instance
        public_id: School's public ID
    Returns:
        Dict containing either school URN ID or error information
    """
    try:
        logger.info(f"Retrieving school information for public_id: {public_id}")
        school = linkedin.get_school(public_id=public_id)
        urn_id = get_id_from_urn(school['entityUrn'])
        result = {
            "success": True,
            "school_urn_id": urn_id,
            "timestamp": "2024-12-10T22:07:56-05:00",
            "public_id": public_id
        }
    except Exception as e:
        logger.error(f"Error retrieving school information: {str(e)}")
        result = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "error_traceback": traceback.format_exc(),
            "timestamp": "2024-12-10T22:07:56-05:00",
            "public_id": public_id
        }
    
    with open("v2_search/input/school.json", "w") as f:
        json.dump(result, f, indent=4)
    return result

if __name__ == "__main__":
    import json, os
    linkedin = LinkedinWrapper("productionadamh@gmail.com", "gptproject135764", debug=True)

    with open("v2_search/input/helper.json", "r") as f:
        params = json.load(f)
    
    if params['function'] == "get_company":
        get_company(
            linkedin=linkedin,
            public_id=params['input']
        )    
    elif params['function'] == "get_school":
        get_school(
            linkedin=linkedin,
            public_id=params['input']
        )   