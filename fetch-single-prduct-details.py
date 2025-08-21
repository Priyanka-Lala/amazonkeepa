import requests
import csv
import time
import base64
import json

KEEPA_API_KEY = 'o4eilsi0lhfttrantu7cvpe9kfu2afhl46qc0n3b4r03tatabb09c4l89mjh748r'  # Replace with your real API key
DOMAIN_ID = 1  # US Marketplace

def ask_category():
    print("\n✅ Choose a category:")
    categories = {
        1: ("Home & Kitchen", 284507),
        2: ("Office Products", 1064954),
        3: ("Pet Supplies", 2619533011),
        4: ("Baby", 165796011),
        5: ("Sports & Outdoors", 3375251),
        6: ("Tools & Home Improvement", 228013),
        7: ("Beauty & Personal Care", 3760911)
    }
    for key, (name, _) in categories.items():
        print(f"{key}. {name}")

    choice = int(input("Enter category number: "))
    return categories.get(choice)

# def ask_price_range():
#     print("\n✅ Enter price range in cents (e.g., 2000 = $20)")
#     min_price = int(input("Enter minimum price: "))
#     max_price = int(input("Enter maximum price: "))
#     return min_price, max_price

def ask_size_filter():
    print("\n✅ Optional size/weight limits (in grams and mm). Press Enter to skip any field.")
    try:
        weight_max = int(input("Max weight (g): ") or 0)
        length_max = int(input("Max length (mm): ") or 0)
        width_max = int(input("Max width (mm): ") or 0)
        height_max = int(input("Max height (mm): ") or 0)
    except ValueError:
        weight_max = length_max = width_max = height_max = 0
    return weight_max, length_max, width_max, height_max

def ask_title_keywords():
    print("\n✅ Optional keyword filter")
    keyword = input("Enter keyword to include in title (or press Enter to skip): ")
    return keyword

def fetch_products(category_id,  weight, length, width, height, keyword):
    print("\n🔍 Fetching ASINs from Keepa...")

    query_json = {
        "category": category_id,
        # "priceMin": price_min,
        # "priceMax": price_max,
        "salesRankMax": 125000,
        "dropsMin": 30,
        "condition": 1,
        "fbaSellerCountMin": 3,
        "fbaSellerCountMax": 15,
        "page": 0
    }

    if weight > 0:
        query_json['packageWeightMax'] = weight
    if length > 0:
        query_json['packageLengthMax'] = length
    if width > 0:
        query_json['packageWidthMax'] = width
    if height > 0:
        query_json['packageHeightMax'] = height
    if keyword:
        query_json['title'] = keyword

    query_encoded = base64.b64encode(json.dumps(query_json).encode()).decode()
    url = f"https://api.keepa.com/query?key={KEEPA_API_KEY}&domain=1&query={query_encoded}"
    response = requests.get(url)
    data = response.json()

    asins = [p['asin'] for p in data.get("products", [])]
    return asins

def fetch_product_details(asins):
    print("\n📦 Fetching product details...")
    product_data = []
    for asin in asins:
        url = f"https://api.keepa.com/product?key={KEEPA_API_KEY}&domain=1&asin={asin}&stats=180"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            if data.get('products'):
                p = data['products'][0]
                product_data.append({
                    'asin': asin,
                    'title': p.get('title', 'N/A'),
                    'brand': p.get('brand', 'N/A'),
                    'price': p.get('buyBoxPrice') or p.get('amazon', 'N/A'),
                    'bsr': p.get('salesRank', 'N/A'),
                    'fba_sellers': p.get('fbaSellerCount', 'N/A')
                })
        time.sleep(1)  # avoid hitting rate limits
    return product_data

def save_to_csv(products):
    filename = f"keepa_detailed_products_{int(time.time())}.csv"
    print(f"\n💾 Saving results to {filename}...")

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['asin', 'title', 'brand', 'price', 'bsr', 'fba_sellers'])
        writer.writeheader()
        for product in products:
            writer.writerow(product)

    print("✅ Done!")

# ------------------ MAIN ------------------ #

if __name__ == "__main__":
    cat_info = ask_category()
    if not cat_info:
        print("❌ Invalid category.")
        exit()

    cat_name, cat_id = cat_info
    #price_min, price_max = ask_price_range()
    weight, length, width, height = ask_size_filter()
    keyword = ask_title_keywords()

    asins = fetch_products(
        category_id=cat_id,
        # price_min=price_min,
        # price_max=price_max,
        weight=weight,
        length=length,
        width=width,
        height=height,
        keyword=keyword
    )

    if asins:
        detailed_products = fetch_product_details(asins)
        save_to_csv(detailed_products)
    else:
        print("❌ No products found. Try relaxing some filters.")
