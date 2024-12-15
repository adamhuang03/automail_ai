from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
from openai import OpenAI
from typing import List, Dict
import csv
from io import StringIO
import logging
import asyncio
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

# Import from the lib directory relative to vercel_python
from lib.automail_ai_craft import draft_email, enrich_person, multi_enrich_persons
from lib.linkedin_wrapper import LinkedinWrapper

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
            
            # Initialize LinkedIn client
            logger.info("Initializing LinkedIn client")
            linkedin_client = LinkedinWrapper(
                username=os.getenv("LINKEDIN_USER"),
                password=os.getenv("LINKEDIN_PASSWORD"),
                debug=True
            )

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
