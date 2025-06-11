import requests
import pandas as pd
import time
from datetime import datetime
import logging
from typing import List, Dict, Any
import sys
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_URL = "https://api.ycombinator.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.ycombinator.com",
    "Referer": "https://www.ycombinator.com/companies",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "x-request-source": "companies-page",
    "x-operation-name": "CompanySearch"
}

# Filtered GraphQL query
filtered_query = """
query CompanySearch($searchQuery: CompanySearchQuery!) {
  companySearch(query: $searchQuery) {
    companies {
      name
      slug
      website
      location
    }
    total
  }
}
"""

# Detailed company info query
detail_query = """
query CompanyPage($slug: String!) {
  company(slug: $slug) {
    name
    location
    teamSize
    website
    linkedin
    founders {
      name
      linkedin
    }
  }
}
"""

# Search query structure
search_query = {
    "searchQuery": {
        "query": "",
        "filters": {
            "batch": ["Winter 2025", "Fall 2024", "Summer 2024"],
            "regions": [
                "United States of America", "United Kingdom", "France",
                "Germany", "Switzerland", "Netherlands",
                "United Arab Emirates", "Australia"
            ],
            "teamSize": ["1-5"]
        },
        "sortBy": "recently_added",
        "page": 1
    }
}

def make_request(url: str, payload: Dict[str, Any], retry_count: int = 3) -> Dict[str, Any]:
    """Make a request with retry logic and error handling"""
    for attempt in range(retry_count):
        try:
            response = requests.post(url, headers=HEADERS, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                logging.error(f"GraphQL Error: {data['errors']}")
                raise Exception(f"GraphQL Error: {data['errors']}")
                
            return data
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == retry_count - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
    return {}

def fetch_companies() -> List[Dict[str, Any]]:
    """Fetch all companies matching the filters"""
    all_data = []
    
    for batch_num in range(1, 20):  # Pagination
        logging.info(f"Fetching filtered companies, batch {batch_num}")
        
        try:
            # Update page number in search query
            current_query = search_query.copy()
            current_query["searchQuery"]["page"] = batch_num
            
            payload = {
                "query": filtered_query,
                "variables": current_query
            }
            
            data = make_request(BASE_URL, payload)
            companies = data.get("data", {}).get("companySearch", {}).get("companies", [])
            
            if not companies:
                logging.info(f"No more companies found after batch {batch_num}")
                break
                
            for company in companies:
                try:
                    company_data = fetch_company_details(company["slug"])
                    if company_data:
                        all_data.append(company_data)
                        logging.info(f"Successfully fetched data for {company['name']}")
                except Exception as e:
                    logging.error(f"Error fetching details for {company.get('slug', 'unknown')}: {str(e)}")
                
                time.sleep(1)  # Rate limiting prevention
                
        except Exception as e:
            logging.error(f"Error fetching batch {batch_num}: {str(e)}")
            break
            
        logging.info(f"Completed batch {batch_num} with {len(companies)} companies")
    
    return all_data

def fetch_company_details(slug: str) -> Dict[str, Any]:
    """Fetch detailed information for a single company"""
    detail_payload = {
        "query": detail_query,
        "variables": {"slug": slug}
    }
    
    data = make_request(BASE_URL, detail_payload)
    details = data.get("data", {}).get("company", {})
    founders = details.get("founders", [])
    
    return {
        "Company Name": details.get("name"),
        "Location": details.get("location"),
        "Team Size": details.get("teamSize"),
        "Website": details.get("website"),
        "LinkedIn Page": details.get("linkedin"),
        "Founders": ", ".join(f.get("name", "") for f in founders if f.get("name")),
        "Founders LinkedIn": ", ".join(f.get("linkedin", "") for f in founders if f.get("linkedin"))
    }

def main():
    try:
        logging.info("Starting YC company scraper...")
        
        all_data = fetch_companies()
        
        if not all_data:
            logging.error("No data was collected!")
            return
            
        # Save results with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"yc_filtered_companies_{timestamp}.csv"
        
        df = pd.DataFrame(all_data)
        df.to_csv(filename, index=False)
        
        logging.info(f"✅ Done! Saved {len(all_data)} companies to {filename}")
        logging.info(f"Data preview:\n{df.head()}")
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
