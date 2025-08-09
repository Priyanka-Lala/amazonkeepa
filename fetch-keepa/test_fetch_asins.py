import requests
import csv
import time

# Your Keepa API key (replace with your own)
API_KEY = "o4eilsi0lhfttrantu7cvpe9kfu2afhl46qc0n3b4r03tatabb09c4l89mjh748r"

# Search settings
DOMAIN_ID = 1  # 1 = Amazon.com (US)
SEARCH_TERM = "curtain"  # Replace with your desired keyword
OUTPUT_FILE = "search_asins_output.csv"

# Save only ASINs to reduce token usage
ASINS_ONLY = 1
MAX_PAGES = 10  # Pages 0 through 9 (max 100 results)

def fetch_asins():
    all_asins = []

    for page in range(MAX_PAGES):
        print(f"🔍 Fetching page {page} for '{SEARCH_TERM}'...")
        url = (
            f"https://api.keepa.com/search"
            f"?key={API_KEY}"
            f"&domain={DOMAIN_ID}"
            f"&type=product"
            f"&term={SEARCH_TERM}"
            f"&asins-only={ASINS_ONLY}"
            f"&page={page}"
        )

        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code} - {response.text}")
            break

        data = response.json()
        if 'asinList' not in data or len(data['asinList']) == 0:
            print("ℹ️ No more results.")
            break

        all_asins.extend(data['asinList'])

        # If less than 10 results returned, it's the last page
        if len(data['asinList']) < 10:
            break

        time.sleep(2)  # Respect API rate limits

    # Save to CSV
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ASIN", "Title"])
        for asin in all_asins:
            asin = product.get("asin", "")
            title = product.get("title", "")
            writer.writerow([asin, title])

    print(f"\n✅ Fetched {len(all_asins)} ASINs and saved to '{OUTPUT_FILE}'.")

if __name__ == "__main__":
    fetch_asins()
