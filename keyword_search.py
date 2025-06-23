#starting with the search_bill coding for keyword search
def search_bill(keyword):
    """
    Simulates searching for bills based on a keyword.
    For Version 1, this will return hardcoded data.
    """
    print(f"Searching for bills with the keyword: '{keyword}'...")

    # Hardcoded Data for Simulation (V1) 
    if "climate" in keyword.lower():
        # Example data based on ProPublica Congress API structure
        return [
            {"title": "Clean Air Act Amendment of 2025", "status": "Passed House, Awaiting Senate Vote", "bill_id": "hr3684"},
            {"title": "Climate Change Mitigation Bill", "status": "Introduced", "bill_id": "s1234"},
        ]
    elif "education" in keyword.lower():
        return [
            {"title": "Student Loan Forgiveness Act", "status": "In Committee", "bill_id": "hr5678"}
        ]
    else:
        return []

if __name__ == "__main__":
    print("Welcome to LexLearner CLI (Version 1 - Simulation Mode)")
    user_input = input("Enter a keyword to search for bills (e.g., 'climate', 'education'): ")

    results = search_bill(user_input)

    if results:
        print("\n--- Search Results ---")
        for bill in results:
            print(f"Title: {bill['title']}")
            print(f"Status: {bill['status']}")
            print(f"Bill ID: {bill['bill_id']}")
            print("-" * 20)
    else:
        print(f"There were no bills found for '{user_input}'. Please try again.")
