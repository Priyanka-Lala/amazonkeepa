import keepa
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union

# -----------------------------------------------------------
# 1. ADD YOUR KEEPA API KEY HERE
# -----------------------------------------------------------
KEEPA_API_KEY = "o4eilsi0lhfttrantu7cvpe9kfu2afhl46qc0n3b4r03tatabb09c4l89mjh748r"  # Replace with your Keepa API key


# -----------------------------------------------------------
# 2. HELPER FUNCTIONS
# -----------------------------------------------------------

def get_latest_price(price_data: Optional[Union[List, np.ndarray]]) -> Optional[float]:
    """
    Extract the latest non-zero price from Keepa price list (in cents).
    Returns price in dollars.
    """
    if price_data is None:
        return None

    # Convert numpy array to list if needed
    if isinstance(price_data, np.ndarray):
        price_data = price_data.tolist()

    if not isinstance(price_data, list) or len(price_data) == 0:
        return None

    # Iterate backwards for last non-zero scalar price
    for price in reversed(price_data):
        if isinstance(price, (int, float)) and price > 0:
            return price / 100.0
    return None


def get_price_stability(product_data: Dict, data_key: str) -> str:
    """
    Check if price is stable over the last 30 days (variation < 5%).
    """
    try:
        stability_data = product_data.get("data", {}).get(data_key)
        if stability_data is None:
            return "N/A"

        # Convert numpy arrays to list
        if isinstance(stability_data, np.ndarray):
            stability_data = stability_data.tolist()

        if not isinstance(stability_data, list) or len(stability_data) == 0:
            return "N/A"

        # Take last 30 data points for recent prices
        recent_prices = [p for p in stability_data[-30:] if isinstance(p, (int, float)) and p > 0]

        if len(recent_prices) < 2:
            return "N/A"

        min_price = min(recent_prices)
        max_price = max(recent_prices)

        if min_price == 0:
            return "N/A"

        variation = ((max_price - min_price) / min_price) * 100
        return "Y" if variation < 5 else "N"

    except Exception:
        return "N/A"


def calculate_metrics(amazon_price: Optional[float], source_price: Optional[float]) -> Dict[str, Union[str, float]]:
    """
    Calculates profit and ROI based on buy and sell prices.
    """
    if amazon_price is None or source_price is None:
        return {"ROI (%)": "N/A", "Profit ($)": "N/A"}

    # Example FBA fees (replace with your own calculations)
    fba_fees = 0.15 * amazon_price + 3.00

    profit = amazon_price - source_price - fba_fees
    roi = (profit / source_price) * 100 if source_price > 0 else 0

    return {
        "ROI (%)": f"{roi:.2f}%",
        "Profit ($)": f"${profit:.2f}"
    }


def get_estimated_monthly_sales(bsr: Optional[int], category: str) -> Optional[int]:
    """
    Estimates monthly sales based on BSR and category.
    NOTE: This is a simplified estimation and should be replaced with a more accurate model.
    """
    if bsr is None:
        return None

    # Placeholder logic for estimation
    if bsr < 1000:
        return 100
    elif bsr < 5000:
        return 50
    elif bsr < 10000:
        return 20
    else:
        return 5


# -----------------------------------------------------------
# 3. CORE PROCESSING FUNCTION
# -----------------------------------------------------------

def get_product_data(asins: List[str], api_key: str) -> List[Dict[str, Any]]:
    """
    Retrieve product data from Keepa API and process it.
    """
    products_data = []

    try:
        api = keepa.Keepa(api_key)
        products = api.query(asins, domain='US', stats=1)

        print(f"Debug: API returned {len(products)} products for {len(asins)} ASINs.")

        for i, asin in enumerate(asins):
            product = products[i] if i < len(products) else None

            # Case 1: Product data is completely missing or None
            if product is None:
                products_data.append({
                    "ASIN": asin, "Product Title": "Product not found", "Amazon Buy Price": "N/A",
                    "Source Buy Price": "N/A", "Source URL": f"https://www.amazon.com/dp/{asin}",
                    "Estimated Monthly Sales": "N/A", "BSR": "N/A", "Category": "N/A",
                    "ROI (%)": "N/A", "Profit ($)": "N/A", "Number of Sellers": "N/A",
                    "Hazmat": "N/A", "Gated": "N/A", "Brand Restricted": "N/A",
                    "Keepa Stable": "N/A", "Notes": "Product not found in Keepa database or API error"
                })
                print(f"⚠️ ASIN {asin} not found in Keepa. Skipped.")
                continue

            try:
                title = product.get("title", "N/A")

                amazon_price = get_latest_price(product.get("data", {}).get("AMAZON", []))
                source_price = get_latest_price(product.get("data", {}).get("BUY_BOX_SHIPPING", []))

                # Fallback to NEW price if BUY_BOX_SHIPPING not found
                if not source_price:
                    source_price = get_latest_price(product.get("data", {}).get("NEW", []))

                # Fallback to amazon price if no source price found
                if not source_price and amazon_price:
                    source_price = amazon_price

                bsr = None
                sales_ranks = product.get("salesRanks")
                if sales_ranks and "SALES" in sales_ranks:
                    try:
                        # Sales ranks are usually lists of [timestamp, rank]
                        bsr = sales_ranks["SALES"][-1][1]
                    except (IndexError, KeyError, TypeError):
                        pass

                metrics = calculate_metrics(amazon_price, source_price)
                num_sellers = product.get("offerCount", "N/A")

                keepa_stable = get_price_stability(product, "AMAZON")
                if keepa_stable == "N/A":
                    keepa_stable = get_price_stability(product, "NEW")

                products_data.append({
                    "ASIN": asin,
                    "Product Title": title,
                    "Amazon Buy Price": f"${amazon_price:.2f}" if amazon_price is not None else "N/A",
                    "Source Buy Price": f"${source_price:.2f}" if source_price is not None else "N/A",
                    "Source URL": f"https://www.amazon.com/dp/{asin}",
                    "Estimated Monthly Sales": get_estimated_monthly_sales(bsr, product.get("productGroup", "")) if bsr else "N/A",
                    "BSR": bsr if bsr else "N/A",
                    "Category": product.get("productGroup", "N/A"),
                    "ROI (%)": metrics["ROI (%)"],
                    "Profit ($)": metrics["Profit ($)"],
                    "Number of Sellers": num_sellers,
                    "Hazmat": "N/A",
                    "Gated": "N/A",
                    "Brand Restricted": "N/A",
                    "Keepa Stable": keepa_stable,
                    "Notes": ""
                })

                print(f"✅ Processed {asin}: {title[:50]}...")

            except Exception as e:
                products_data.append({
                    "ASIN": asin,
                    "Product Title": "Error processing product",
                    "Amazon Buy Price": "N/A",
                    "Source Buy Price": "N/A",
                    "Source URL": f"https://www.amazon.com/dp/{asin}",
                    "Estimated Monthly Sales": "N/A",
                    "BSR": "N/A",
                    "Category": "N/A",
                    "ROI (%)": "N/A",
                    "Profit ($)": "N/A",
                    "Number of Sellers": "N/A",
                    "Hazmat": "N/A",
                    "Gated": "N/A",
                    "Brand Restricted": "N/A",
                    "Keepa Stable": "N/A",
                    "Notes": f"Error: {str(e)}"
                })
                print(f"❌ Error processing ASIN {asin}: {e}")

    except keepa.APIException as e:
        print(f"❌ Keepa API Error: {e}")
    except Exception as e:
        print(f"❌ General Error: {e}")

    return products_data


# -----------------------------------------------------------
# 4. MAIN FUNCTION
# -----------------------------------------------------------

def main():
    print("🚀 Starting Keepa Product Analysis...")

    # Define your product finder parameters here
    finder_params = {
        'category': 1055398,  # Home & Kitchen
        'salesRankDrops_min': 1,
        'current_salesrank_min': 1,
        'current_salesrank_max': 10000,
        'isEligibleForPrime': [1],
        'current_NEW_min': 1000,  # Price in cents, so 1000 = $10.00
        'sortBy': 'current_SALES_RANK',
        'sortOrder': 'asc',
        'limit': 50
    }

    try:
        api = keepa.Keepa(KEEPA_API_KEY)
        print("🔍 Searching for products with the following criteria:", finder_params)
        asins = api.product_finder(finder_params, domain='US')
        print(f"✅ Product Finder found {len(asins)} ASINs.")

        if asins:
            print(f"📊 Processing {len(asins)} ASINs...")
            products_data = get_product_data(asins, KEEPA_API_KEY)

            df = pd.DataFrame(products_data)
            output_filename = "keepa_product_analysis.csv"
            df.to_csv(output_filename, index=False)

            print(f"✅ Data exported to {output_filename}")
            print(f"📈 Final data shape: {df.shape}")
        else:
            print("❌ No ASINs found matching the criteria.")

    except keepa.APIException as e:
        print(f"❌ Keepa API Exception: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
