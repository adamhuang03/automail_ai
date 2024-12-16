from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os
from openai import AsyncOpenAI
import csv
from io import StringIO
import logging
import json
import time
import asyncio

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
from custom_lib.automail_ai_craft import draft_email, enrich_person, multi_enrich_persons, draft_emails_batch
from prompt.email import EMAIL_SYSTEM_PROMPT
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
        start_time = time.time()
        try:
            # Send initial checkpoint
            yield json.dumps({"status": "started", "message": f"Request received (t=0s)"}) + "\n"
            yield json.dumps({"status": "started", "message": f"CSV Data:\n{request.csv_data}\n"}) + "\n"
            yield json.dumps({"status": "started", "message": f"Industry: {request.keyword_industry}\n"}) + "\n"
            yield json.dumps({"status": "started", "message": f"LinkedIn URL: {request.user_linkedin_url}\n"}) + "\n"
            yield json.dumps({"status": "started", "message": f"Email Template: {request.email_template}\n"}) + "\n"
            
            logger.info(f"Starting process_data with industry: {request}")
            
            from dotenv import load_dotenv
            load_dotenv()

            # Initialize OpenAI client
            yield json.dumps({"status": "progress", "message": f"Initializing OpenAI client (t={int(time.time() - start_time)}s)"}) + "\n"
            logger.info("Initializing OpenAI client")
            openai_client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            cookie_dir = 'custom_lib/'

            cookie_repo_1 = CookieRepository(cookies_dir=cookie_dir)
            cookies_1 = cookie_repo_1.get(os.getenv("LINKEDIN_USER"))
            if cookies_1 and isinstance(cookies_1, RequestsCookieJar):
                logger.info("Successfully loaded cookies from repository")
                logger.info(f"Cookie names: {[cookie.name for cookie in cookies_1]}")
            else:
                logger.warning("No valid cookies found in repository")
                cookies_1 = None

            # Initialize LinkedIn client
            yield json.dumps({"status": "progress", "message": f"Initializing LinkedIn client (t={int(time.time() - start_time)}s)"}) + "\n"
            logger.info("Initializing LinkedIn client")
            linkedin_client = LinkedinWrapper(
                username=os.getenv("LINKEDIN_USER"),
                password=os.getenv("LINKEDIN_PASSWORD"),
                cookies=cookies_1,
                authenticate=True,  # Need this to be True to set the cookies
                refresh_cookies=False,  # Don't refresh existing cookies
                debug=True
            )
            
            yield json.dumps({"status": "progress", "message": f"Starting profile enrichment (t={int(time.time() - start_time)}s)"}) + "\n"
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
            
            yield json.dumps({"status": "progress", "message": f"Found {len(list_of_urls)} URLs to process, splitting between 1 client(s) (t={int(time.time() - start_time)}s)"}) + "\n"
            logger.info(f"Found {len(list_of_urls)} URLs to process, splitting {len(list_of_urls)} between clients")
            
            # Create async tasks for both clients
            logger.info("Starting parallel profile enrichment with both clients")
            
            async def process_client(client, urls, client_name, start_time):
                results = multi_enrich_persons(
                    linkedin=client,
                    values=urls,
                    url_value=True
                )
                yield json.dumps({"status": "progress", "message": f"{client_name} enriched {len(results)} profiles (t={int(time.time() - start_time)}s)"}) + "\n"
                yield results  # Yield the results as the last item
            
            # Process URLs with first client
            logger.info("Starting profile enrichment with client")
            multi_result_enriched = None
            async for item in process_client(linkedin_client, list_of_urls, "Client 1", start_time):
                if isinstance(item, str):  # If it's a progress message
                    yield item
                else:  # If it's the results
                    multi_result_enriched = item
            
            yield json.dumps({"status": "progress", "message": f"Successfully enriched {len(multi_result_enriched)} profiles (t={int(time.time() - start_time)}s)"}) + "\n"
            
            # Send checkpoint before email drafting
            yield json.dumps({"status": "drafting", "message": f"Starting email drafting (t={int(time.time() - start_time)}s)"}) + "\n"
            
            # Process emails using batch processing
            logger.info("Starting batch email drafting")
            
            all_emails = []
            total_profiles = len(multi_result_enriched)
            batch_size = 10
            
            for i in range(0, total_profiles, batch_size):
                batch = multi_result_enriched[i:i + batch_size]
                current_batch_size = len(batch)
                logger.info(f"Processing batch {i//batch_size + 1} with {current_batch_size} profiles")
                yield json.dumps({
                    "status": "progress", 
                    "message": f"Processing email batch {i//batch_size + 1}/{(total_profiles + batch_size - 1)//batch_size} (t={int(time.time() - start_time)}s)"
                }) + "\n"
                
                # Create tasks for the batch
                tasks = []
                for candidate_profile in batch:
                    messages = [
                        {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
                        {"role": "user", "content": f"""
                            User Profile:
                        {json.dumps(user_profile, indent=2)}

                        Candidate Profile:
                        {json.dumps(candidate_profile, indent=2)}

                        Num: 1
                        Role: {request.keyword_industry}
                        Email template:
                        {request.email_template}
                        """}
                    ]
                    
                    tasks.append(
                        openai_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages,
                            temperature=0.7,
                            max_tokens=500
                        )
                    )
                
                # Process batch concurrently
                batch_responses = await asyncio.gather(*tasks)
                batch_emails = [response.choices[0].message.content for response in batch_responses]
                all_emails.extend(batch_emails)
                
                logger.info(f"Completed batch {i//batch_size + 1}, total emails: {len(all_emails)}/{total_profiles}")
                yield json.dumps({
                    "status": "progress",
                    "message": f"Completed {len(all_emails)}/{total_profiles} emails (t={int(time.time() - start_time)}s)"
                }) + "\n"
            
            emails = all_emails
            
            # Send checkpoint before email drafting
            yield json.dumps({"status": "drafting", "message": f"Adding enriched data to CSV (t={int(time.time() - start_time)}s)"}) + "\n"
            
            # Add enriched data to CSV
            logger.info("Adding enriched data to CSV")
            for i in range(len(csv_data_list[1:])):  # Skip header
                email_data = emails[i]
                csv_data_list[i+1][6] = email_data
            
            yield json.dumps({"status": "drafting", "message": f"Preparing final CSV (t={int(time.time() - start_time)}s)"}) + "\n"
            
            # Prepare final CSV response
            output_csv = StringIO()
            csv_writer = csv.writer(output_csv)
            csv_writer.writerows(csv_data_list)
            
            # Send final CSV data
            yield json.dumps({
                "status": "completed",
                "message": f"Process completed (t={int(time.time() - start_time)}s)",
                "csv_data": output_csv.getvalue()
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Error in process_data: {str(e)}", exc_info=True)
            yield json.dumps({
                "status": "error",
                "message": f"Error (t={int(time.time() - start_time)}s): {str(e)}"
            }) + "\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream"
    )

@app.get("/")
async def root():
    return {"message": "AutoMail AI API is running"}
