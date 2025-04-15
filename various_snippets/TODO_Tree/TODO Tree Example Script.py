# TODO: Add logging to track function calls

def fetch_data_from_api(url):
    # NOTE: This function simulates an API call
    print(f"Fetching data from {url}")
    return {"status": "success", "data": [1, 2, 3, 4]}

# FIXME: Handle the case where data is None
def process_data(data):
    if data:
        processed = [x * 2 for x in data["data"]]
        return processed
    else:
        return []

# [ ] Add unit tests for process_data
# [x] Initial version of fetch_data_from_api complete

def main():
    url = "https://api.example.com/data"
    data = fetch_data_from_api(url)
    results = process_data(data)
    print("Processed:", results)

# HACK: Temporary workaround for API timeout issues
# IMPROVE: Add retry logic with exponential backoff

if __name__ == "__main__":
    main()

# CLEANUP: Remove hardcoded URL before deployment
# FUNCTION: main
# BUG: This will break if the API response format changes
# DELETE: Old data caching logic from previous version
