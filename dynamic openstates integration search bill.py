# purpose of this file is to plug in and test the search of OpenStates data for given parameters

import requests
from keys import OPENSTATES_API_KEY # Ensure your OpenStates API key is in keys.py

# Base URL for the OpenStates v3 API
OPENSTATES_BASE_URL = "https://v3.openstates.org"

def search_bill_openstates(keyword, jurisdiction="ga", session="current", limit=20):
    """
    Searches for bills using the OpenStates v3 API (Plural).
    Fetches results based on a keyword and jurisdiction, then retrieves
    additional details like subjects and abstract for each bill.

    Args:
        keyword (str): The search term for the bill title or description.
        jurisdiction (str): The state or territory abbreviation (e.g., "ga" for Georgia).
                            Defaults to "ga" if not specified.
        session (str): The legislative session (e.g., "2023-2024"). Defaults to "current".
        limit (int): The maximum number of bills to fetch per page. Defaults to 20.

    Returns:
        list: A list of dictionaries, each representing a formatted bill with
              title, status, subjects, abstract, OpenStates URL, and classification.
    """
    print(f"Searching for bills with keyword: '{keyword}' in {jurisdiction.upper()} "
          f"(Session: {session}) using OpenStates API...")

    headers = {"X-API-KEY": OPENSTATES_API_KEY}
    search_url = f"{OPENSTATES_BASE_URL}/bills"

    params = {
        "q": keyword,
        "jurisdiction": jurisdiction.lower(),
        "session": session,
        "classification": "bill", # Ensure we're only getting bills
        "sort": "latest_action_desc", # Sort by most recent action first
        "page": 1,
        "per_page": limit
    }

    formatted_results = []

    try:
        # First API call: Search for bills
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()

        bills_found = data.get("results", [])

        if not bills_found:
            print(f"No initial bills found for '{keyword}' in {jurisdiction.upper()}.")
            return []

        # Second API call (for each bill): Fetch detailed information
        # This makes multiple requests, one for each bill, to get more data.
        for i, bill in enumerate(bills_found):
            if i >= limit: # Respect the limit, even if API returned more initially
                break

            bill_id = bill["id"] # OpenStates unique ID for the bill
            detail_url = f"{OPENSTATES_BASE_URL}/bills/{bill_id}"
            
            detail_resp = requests.get(detail_url, headers=headers)
            detail_resp.raise_for_status()
            detail_data = detail_resp.json()

            # Extract and format relevant data for the general user
            title = detail_data.get("title", "N/A")
            identifier = detail_data.get("identifier", "N/A") # e.g., "HB 123"
            
            # Get the latest action text for status
            latest_action_text = "No recent action found."
            actions = detail_data.get("actions", [])
            if actions:
                # Actions are usually sorted by date in descending order, last one is latest
                latest_action_text = actions[-1].get("description", "No description.")

            # Subjects for categorization (e.g., "Environment", "Civil Rights")
            subjects = [s.get("name", "") for s in detail_data.get("subjects", []) if s.get("name")]
            abstract_text = detail_data.get("abstract", "No abstract available.")
            openstates_url = detail_data.get("openstates_url", "No URL available.")
            
            # Classification (e.g., "bill", "resolution")
            classification = detail_data.get("classification", "N/A")


            formatted_results.append({
                "identifier": identifier,
                "title": title,
                "status": latest_action_text,
                "subjects": ", ".join(subjects) if subjects else "N/A", # Formatted for display
                "abstract": abstract_text,
                "openstates_url": openstates_url,
                "classification": classification
            })
        return formatted_results

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} (Status code: {response.status_code})")
        if response.status_code == 401 or response.status_code == 403:
            print("Please check if your OpenStates API key is correct and valid.")
        return []
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        print("Please check your internet connection.")
        return []
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
        print("The API server took too long to respond.")
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected request error occurred: {req_err}")
        return []
    except KeyError as e:
        print(f"Error parsing API response. Missing expected key: {e}")
        print(f"Partial data for debugging: {data}")
        return []
    except Exception as e:
        print(f"An unknown error occurred: {e}")
        return []


if __name__ == "__main__":
    print("Welcome to LexLearner CLI (OpenStates v3 API)")
    print("Making legal data accessible to everyone.")

    while True:
        keyword_input = input("\nEnter a keyword to search for bills (e.g., 'education', 'tax', 'health', or 'exit' to quit): ").strip()
        if keyword_input.lower() == 'exit':
            break
        if not keyword_input:
            print("Please enter a valid keyword.")
            continue

        jurisdiction_input = input("Enter a state/territory abbreviation (e.g., 'ga' for Georgia, 'ny' for New York, 'all' for all available states, or leave blank for 'ga'): ").strip().lower()
        if not jurisdiction_input:
            jurisdiction_input = "ga" # Default to Georgia

        print("-" * 50)
        results = search_bill_openstates(keyword_input, jurisdiction_input)

        if results:
            print("\n--- Search Results ---")
            for bill in results:
                print(f"Bill ID: {bill['identifier']}")
                print(f"Title: {bill['title']}")
                print(f"Type: {bill['classification'].replace('_', ' ').title()}") # e.g., "Senate Bill", "Resolution"
                print(f"Status: {bill['status']}")
                print(f"Subjects: {bill['subjects']}") # The "categories" like "Environment", "Civil Rights"
                
                abstract_lines = [line.strip() for line in bill['abstract'].split('.') if line.strip()]
                print("Abstract:")
                for line in abstract_lines:
                    print(f"  - {line}.")
                print(f"View Full Bill: {bill['openstates_url']}") # Direct link to the bill
                print("-" * 50)
        else:
            print(f"No bills found for '{keyword_input}' in {jurisdiction_input.upper()}. Please try a different keyword or jurisdiction.")

    print("Exiting LexLearner. Goodbye!")