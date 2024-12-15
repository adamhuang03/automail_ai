from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
from openai import OpenAI
import csv
from io import StringIO
import logging
import json

import sys
from pathlib import Path
# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.hasHandlers():  # Avoid adding handlers multiple times
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Import from the custom_lib directory relative to vercel_python
from custom_lib.automail_ai_craft import draft_email, enrich_person, multi_enrich_persons
from custom_lib.linkedin_wrapper import LinkedinWrapper
from requests.cookies import RequestsCookieJar
from linkedin_api.cookie_repository import CookieRepository

# uvicorn vercel_python.api.index:app --reload --log-level info

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request model
class ProcessDataRequest(BaseModel):
    csv_data: str
    keyword_industry: str
    user_linkedin_url: str
    email_template: str

@app.post("/process-data")
async def process_data(request: ProcessDataRequest):
    async def generate_response():
        try:
            # Send initial checkpoint
            yield json.dumps({"status": "started", "message": "Request received"}) + "\n"
            
            logger.info(f"Starting process_data with industry: {request}")
            
            from dotenv import load_dotenv
            load_dotenv()

            # Initialize OpenAI client
            logger.info("Initializing OpenAI client")
            openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Load cookies from .jr file using CookieRepository
            try:
                cookie_dir = 'custom_lib/'
                cookie_file = os.path.join(cookie_dir, f"{os.getenv('LINKEDIN_USER')}.jr")
                logger.info(f"Looking for cookie file at: {cookie_file}")
                logger.info(f"Current working directory: {os.getcwd()}")
                
                # Check if directory exists
                if os.path.exists(cookie_dir):
                    logger.info(f"Directory {cookie_dir} exists")
                    files = os.listdir(cookie_dir)
                    logger.info(f"Files in {cookie_dir}: {files}")
                else:
                    logger.error(f"Directory {cookie_dir} does not exist")
                    # List contents of current directory
                    files = os.listdir('.')
                    logger.info(f"Files in current directory: {files}")

                # Check if file exists
                if os.path.exists(cookie_file):
                    logger.info(f"Cookie file found at {cookie_file}")
                    file_size = os.path.getsize(cookie_file)
                    logger.info(f"Cookie file size: {file_size} bytes")
                else:
                    logger.error(f"Cookie file not found at {cookie_file}")

                cookie_repo = CookieRepository(cookies_dir=cookie_dir)
                cookies = cookie_repo.get(os.getenv("LINKEDIN_USER"))
                if cookies and isinstance(cookies, RequestsCookieJar):
                    logger.info("Successfully loaded cookies from repository")
                    logger.info(f"Cookie names: {[cookie.name for cookie in cookies]}")
                else:
                    logger.warning("No valid cookies found in repository")
                    cookies = None
            except Exception as e:
                logger.error(f"Error loading cookies: {str(e)}")
                logger.error(f"Error type: {type(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                cookies = None

            # Initialize LinkedIn client
            logger.info("Initializing LinkedIn client")
            linkedin_client = LinkedinWrapper(
                username=os.getenv("LINKEDIN_USER"),
                password=os.getenv("LINKEDIN_PASSWORD"),
                cookies=cookies,
                authenticate=False,
                debug=True
            )
            
            # Log cookie information
            cookies = linkedin_client._cookies()
            if cookies:
                cookie_names = [cookie.name for cookie in cookies]
                logger.info(f"LinkedIn cookies found: {', '.join(cookie_names)}")
            else:
                logger.warning("No LinkedIn cookies available")
            
            logger.info(f"Enriching user profile: {request.user_linkedin_url}")
            user_profile = enrich_person(
                linkedin=linkedin_client,
                value=request.user_linkedin_url,
                url_value=True
            )
            
            # Parse CSV data
            logger.info("Parsing CSV data")
            csv_reader = csv.reader(StringIO(request.csv_data))
            csv_data_list = [row for row in csv_reader]
            
            # Get the URNs (first column)
            list_of_urls = [row[3] for row in csv_data_list[1:]]  # Skip header
            logger.info(f"Found {len(list_of_urls)} URLs to process")
            
            # Enrich the profiles using the imported function
            logger.info("Starting bulk profile enrichment")
            multi_result_enriched = multi_enrich_persons(
                linkedin=linkedin_client,
                values=list_of_urls,
                url_value=True
            )
            logger.info(f"Successfully enriched {len(multi_result_enriched)} profiles")
            
            # Send checkpoint before email drafting
            yield json.dumps({"status": "drafting", "message": "Starting email drafting"}) + "\n"
            
            # Process emails using the imported function
            logger.info("Starting email drafting")
            emails = []
            for i, enriched_person in enumerate(multi_result_enriched, 1):
                logger.debug(f"Drafting email {i}/{len(multi_result_enriched)}")
                email = draft_email(
                    openai=openai_client,
                    user_profile=user_profile,
                    candidate_profile=enriched_person,
                    keyword_industry=request.keyword_industry,
                    email_template=request.email_template
                )
                emails.append(email)
                
                # Send progress update every few emails
                if i % 5 == 0 or i == len(multi_result_enriched):
                    yield json.dumps({
                        "status": "progress",
                        "message": f"Drafted {i}/{len(multi_result_enriched)} emails"
                    }) + "\n"
            
            logger.info(f"Successfully drafted {len(emails)} emails")
            
            # Add enriched data to CSV
            logger.info("Adding enriched data to CSV")
            for i in range(len(csv_data_list[1:])):  # Skip header
                email_data = emails[i]
                csv_data_list[i+1][6] = email_data
            
            # Prepare final CSV response
            output_csv = StringIO()
            csv_writer = csv.writer(output_csv)
            csv_writer.writerows(csv_data_list)
            
            # Send final CSV data
            yield json.dumps({
                "status": "completed",
                "message": "Process completed",
                "csv_data": output_csv.getvalue()
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Error in process_data: {str(e)}", exc_info=True)
            yield json.dumps({
                "status": "error",
                "message": str(e)
            }) + "\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream"
    )

@app.get("/")
async def root():
    return {"message": "AutoMail AI API is running"}
