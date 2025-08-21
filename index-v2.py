import requests
import json

KEEPA_API_KEY = 'o4eilsi0lhfttrantu7cvpe9kfu2afhl46qc0n3b4r03tatabb09c4l89mjh748r'  # Replace with your Keepa key
DOMAIN_ID = 1  # Amazon US

def ask_category():
    print("\n✅ Choose a category:")
    categories = {
        1: "Home & Kitchen",
        2: "Office Products",
        3: "Pet Supplies",
        4: "Baby (non-gated parts only)",
        5: "Sports & Outdoors",
        6: "Tools & Home Improvement",
        7: "Beauty & Personal Care"
    }
    for key, val in categories.items():
        print(f"{key}. {val}")

    choice = int(input("Enter category number: "))
    return categories.get(choice)

def fetch_product_by_asin(asin):
    print(f"\n🔍 Fetching data for ASIN: {asin}")
    url = (
        f"https://api.keepa.com/product?"
        f"key={KEEPA_API_KEY}&domain={DOMAIN_ID}&asin={asin}"
        f"&stats=180&buybox=1&history=1&rating=1&buyboxseller=1&offers=20"
    )

    res = requests.get(url)
    if res.status_code != 200:
        print("❌ Error fetching data.")
        return

    data = res.json()
    if 'products' not in data or not data['products']:
        print("❌ No product data returned.")
        return

    product = data['products'][0]
    print("\n📦 Product Details:")
    print(f"ASIN: {product.get('asin')}")
    print(f"Title: {product.get('title')}")
    print(f"Brand: {product.get('brand')}")
    print(f"BuyBox Price: {product.get('buyBoxPrice')}")
    print(f"BSR: {product.get('salesRank')}")
    print(f"FBA Sellers: {product.get('fbaSellerCount')}")
    print(f"Rating: {product.get('rating')}")
    print(f"Reviews: {product.get('reviewCount')}")

# ------------------ MAIN ------------------ #

if __name__ == "__main__":
    ask_category()  # not used in filtering here, but included for completeness
    asin = input("\n🔢 Enter ASIN to fetch: ") or "B0B754K6Y8"
    fetch_product_by_asin(asin)
